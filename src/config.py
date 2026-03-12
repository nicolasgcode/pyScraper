from dotenv import load_dotenv
import os

load_dotenv()

BASE_PATH = os.getenv("BASE_PATH")
LOGIN_URL = os.getenv("LOGIN_URL")
USERNAME = os.getenv("LOGIN_USERNAME")
PASSWORD = os.getenv("LOGIN_PASSWORD")

LOGIN_URL = "https://id.osde.com.ar/idaas/mtfim/sps/idaas/login?Target=https%3A%2F%2Fid.osde.com.ar%2Foauth2%2Fauthorize%3Fclient_id%3Deac9e950-a7f0-4131-b06e-6048d64fc447%26stateId%3D1d14e287-f039-4d54-902f-de11be35f1a6&client_id=eac9e950-a7f0-4131-b06e-6048d64fc447&identity_source_ids=60085ca5-4a37-4bbf-bce3-006da1a4c652%2C6d21d2d0-5ed2-4484-98d8-6ab860f64763%2C9bba6623-f75d-489b-9432-5d292c52f902%2Cd5154f93-0a14-4039-8c63-d9b2c5aacd2d&login_hint=%7B%7B%22A%22%3A%22D%22%2C%22B%22%3A%22PRE%22%2C%22C%22%3A%22%22%7D%7D&themeId=79350cc8-5f46-43d2-85ef-4453b2fd2f66"

FILIAL_URL = "https://extranet.osde.com.ar/OSDEExtranet/auth/validar-filial.do?filial=23;{filial_numero}&esTitular=true&rol=010"
