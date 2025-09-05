import requests
from requests.auth import HTTPBasicAuth

from rtedata.tools import Logger
from rtedata.retriever import Retriever
from rtedata.catalog import Catalog

class Client:
  credentials = ["client_id", "client_secret"]
  token_url = "https://digital.iservices.rte-france.com/token/oauth/"
  
  def _get_access_token(self):
    self.logger.info("Generate access token")
    data = {"grant_type": "client_credentials"}
    auth = HTTPBasicAuth(self.client_id, self.client_secret)
    response = requests.post(self.token_url, data=data, auth=auth)

    if response.status_code == 200:
        self.logger.info("Access token generated successfully")
        return response.json()["access_token"]
    else:
        raise Exception(f"Access token error : {response.status_code} - {response.text}")
  
  def retrieve_data(self, start_date: str, end_date: str, data_type: list[str] | str, output_dir: str | None = None):
    if output_dir is None:
      return self.retriever.retrieve(start_date, end_date, data_type)
    else:
      return self.retriever.retrieve(start_date, end_date, data_type, output_dir)

  def __init__(self, client_id: str, client_secret: str):
    self.logger = Logger().logger
    self.catalog = Catalog()

    self.client_id = client_id
    self.client_secret = client_secret
    
    self.token = self._get_access_token()
    self.retriever = Retriever(token=self.token, logger=self.logger, catalog=self.catalog)


