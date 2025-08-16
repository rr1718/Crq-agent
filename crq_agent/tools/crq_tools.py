import os
import logging
import requests
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import triang
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

NVD_API_KEY = os.getenv("NVD_API_KEY")

def query_nvd_api(cve_id: str) -> Dict[str, Any]: #using NVD API
    """
    Fetches CVE details from the NVD API.
    Requires NVD_API_KEY environment variable to be set.
    """
    if not NVD_API_KEY:
        return {"error": "NVD_API_KEY is not set in environment variables."}

    base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    headers = {"apiKey": NVD_API_KEY}
    params = {"cveId": cve_id}

    try:
        response = requests.get(base_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        return {"error": f"Error querying NVD API for {cve_id}: {e}"}

def query_epss_api(cve_id: str) -> float: #using EPSS API
    """
    Fetches EPSS score for a given CVE.
    """
    base_url = "https://api.first.org/v1/epss"
    params = {"cve": cve_id}

    try:
        response = requests.get(base_url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data and data.get("epss") and len(data["epss"]) > 0:
            return float(data["epss"][0]["epss"])
        return 0.0 # Default if no EPSS score found
    except requests.exceptions.RequestException as e:
        logger.warning(f"Error querying EPSS API for {cve_id}: {e}")
        return 0.0

def check_cisa_kev(cve_id: str) -> bool: #using CISA KEV catalog
    """
    Checks if a CVE is in the CISA Known Exploited Vulnerabilities (KEV) catalog.
    """
    kev_url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    try:
        response = requests.get(kev_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        for vulnerability in data.get("vulnerabilities", []):
            if vulnerability.get("cveID") == cve_id:
                return True
        return False
    except requests.exceptions.RequestException as e:
        logger.warning(f"Error fetching CISA KEV catalog: {e}")
        return False

def _get_sample(param: Dict[str, Any]) -> float: #getting a sample from a distribution
    """Helper function to get a sample from a specified distribution."""
    dist_type = param.get("distribution", "triangular").lower()
    min_val, ml_val, max_val = param["min"], param["most_likely"], param["max"]

    c = (ml_val - min_val) / (max_val - min_val)
    return triang.rvs(c=c, loc=min_val, scale=(max_val - min_val))

def run_fair_monte_carlo(fair_parameters: Dict[str, Any], num_simulations: int = 10000) -> List[float]: #running a Monte Carlo simulation
    """
    Runs a Monte Carlo simulation for FAIR risk quantification.
    Each parameter in fair_parameters can specify a 'distribution' ('triangular' or 'pert').
    """
    simulated_losses = []
    for _ in range(num_simulations):
        tef_sample = _get_sample(fair_parameters.get("TEF", {"distribution": "triangular", "min": 0, "most_likely": 0, "max": 0}))
        vuln_sample = _get_sample(fair_parameters.get("Vuln", {"distribution": "triangular", "min": 0, "most_likely": 0, "max": 0}))

        lm_p_dist = fair_parameters.get("LM_Primary", {"distribution": "triangular", "min": 0, "most_likely": 0, "max": 0})
        if "min" not in lm_p_dist: # nested case
            lm_p_sample = 0
            if isinstance(lm_p_dist, dict):
                for p_param in lm_p_dist.values():
                    lm_p_sample += _get_sample(p_param)
        else: # flat case
            lm_p_sample = _get_sample(lm_p_dist)

        lm_s_dist = fair_parameters.get("LM_Secondary", {"distribution": "triangular", "min": 0, "most_likely": 0, "max": 0})
        if "min" not in lm_s_dist: # nested case
            lm_s_sample = 0
            if isinstance(lm_s_dist, dict):
                for s_param in lm_s_dist.values():
                    lm_s_sample += _get_sample(s_param)
        else: # flat case
            lm_s_sample = _get_sample(lm_s_dist)


        lef_sample = tef_sample * vuln_sample
        loss_per_event = lm_p_sample + lm_s_sample
        annualized_loss = lef_sample * loss_per_event
        simulated_losses.append(annualized_loss)

    return simulated_losses

def generate_loss_exceedance_curve_plot(simulation_results: List[float], output_path: str) -> str:
    """
    Generates a Loss Exceedance Curve plot from simulation results.
    """
    if not simulation_results:
        return "Error: No simulation results to plot."

    sorted_losses = np.sort(simulation_results)[::-1]
    exceedance_probabilities = np.arange(1, len(sorted_losses) + 1) / len(sorted_losses)

    plt.figure(figsize=(10, 6))
    plt.plot(sorted_losses, exceedance_probabilities * 100)
    plt.xlabel("Annualized Loss ($)")
    plt.ylabel("Probability of Exceedance (%)")
    plt.title("Loss Exceedance Curve")
    plt.grid(True)
    plt.xscale("log")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    return output_path