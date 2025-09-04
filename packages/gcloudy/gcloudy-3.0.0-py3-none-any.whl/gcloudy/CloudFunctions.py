
import warnings
import subprocess
import pandas as pd
import polars as pl

from google.cloud import bigquery
from google.oauth2 import service_account






class CloudFunctions:

    def __init__(
        self, 
        cf_name, 
        cf_entry_point = None, 
        repo_name = None, 
        repo_source = None, 
        gcp_project_name = None, 
        memory = "8192MB", 
        timeout = "540s", 
        runtime = "python312", 
        custom_service_account = None
    ):
        self.cf_name = cf_name
        self.cf_entry_point = cf_entry_point
        self.repo_name = repo_name
        self.repo_source = repo_source
        self.gcp_project_name = gcp_project_name
        self.memory = memory
        self.timeout = timeout
        self.runtime = runtime
        self.custom_service_account = custom_service_account
        self.__check_mem(self.memory)


    def __check_mem(self, mem):
        mem_allow = ["128MB", "256MB", "512MB", "1024MB", "2048MB", "4096MB", "8192MB"]
        if mem not in mem_allow:
            raise ValueError(f"'memory' arg must be a type string from these options: {', '.join(mem_allow)}")


    def __src_url(self):
        url_prefix = "https://source.developers.google.com/projects/"
        url = f"{url_prefix}{self.gcp_project_name}/repos/{self.repo_source}/moveable-aliases/master/paths/{self.repo_name}"
        return url


    def deploy_http(self):
        url = self.__src_url()
        if self.custom_service_account is None:
            cmnd = f"gcloud functions deploy {self.cf_name} --trigger-http --source {url} --runtime {self.runtime} --entry-point={self.cf_entry_point} --memory={self.memory} --timeout={self.timeout}"
        else:
            cmnd = f"gcloud functions deploy {self.cf_name} --trigger-http --source {url} --runtime {self.runtime} --entry-point={self.cf_entry_point} --memory={self.memory} --timeout={self.timeout} --service-account={self.custom_service_account}"
        execute = subprocess.run(cmnd.split(), stdout = subprocess.PIPE)
        return execute.stdout.decode("utf-8").split("\n")


    def run(self):
        cmnd = f"gcloud functions call {self.cf_name}"
        execute = subprocess.run(cmnd.split(), stdout = subprocess.PIPE)
        stdout_list = execute.stdout.decode("utf-8").split("\n")
        if len(stdout_list) == 1:
            return f"Cloud Function '{self.cf_name}' not found"
        else:
            return stdout_list


    def deploy_http_legacy(self):
        url = self.__src_url()
        if self.custom_service_account is None:
            cmnd = f"""
            gcloud functions deploy {self.cf_name} \
                --trigger-http \
                --source {url} \
                --runtime {self.runtime} \
                --entry-point={self.cf_entry_point} \
                --memory={self.memory} \
                --timeout={self.timeout} \
                --no-gen2
            """
        else:
            cmnd = f"""
            gcloud functions deploy {self.cf_name} \
                --trigger-http \
                --source {url} \
                --runtime {self.runtime} \
                --entry-point={self.cf_entry_point} \
                --memory={self.memory} \
                --timeout={self.timeout} \
                --service-account={self.custom_service_account} \
                --no-gen2
            """
        execute = subprocess.run(cmnd.split(), stdout = subprocess.PIPE)
        return execute.stdout.decode("utf-8").split("\n")


    def deploy_http_gen2(
        self,
        source = None,
        entry_point = "main",
        region = "us-central1",
        n_cpu = 4,
        custom_service_account = None
    ):
        cf_source = {self.cf_name} if source is None else source
        if custom_service_account is None:
            cmnd = f"""
            gcloud functions deploy {self.cf_name}   \
                --gen2                               \
                --source {cf_source}                 \
                --allow-unauthenticated              \
                --trigger-http                       \
                --runtime {self.runtime}             \
                --region {region}                    \
                --entry-point={entry_point}          \
                --memory={self.memory}               \
                --timeout={self.timeout}             \
                --cpu={str(n_cpu)}
            """
        else:
            cmnd = f"""
            gcloud functions deploy {self.cf_name}   \
                --gen2                               \
                --source {cf_source}                 \
                --allow-unauthenticated              \
                --trigger-http                       \
                --runtime {self.runtime}             \
                --region {region}                    \
                --entry-point={entry_point}          \
                --memory={self.memory}               \
                --timeout={self.timeout}             \
                --cpu={str(n_cpu)}                   \
                --service-account={custom_service_account}
            """
        execute = subprocess.run(cmnd.split(), stdout = subprocess.PIPE)
        return execute.stdout.decode("utf-8").split("\n")
