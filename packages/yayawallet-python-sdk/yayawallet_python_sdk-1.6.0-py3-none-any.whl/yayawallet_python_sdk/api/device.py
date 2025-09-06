from ..functions.api_request import api_request

async def get_all_devices(user_id: str, api_key: str = None):
  api_response = await api_request("GET", f"/admin/devices/user/{user_id}", "", None, api_key)
  return api_response

async def deactivate_all_devices( user_id: str, api_key: str = None):
  api_response = await api_request("POST", f"/admin/devices/user/{user_id}/deactivate-all", "", None, api_key)
  return api_response

async def deactivate_device(device_id: str, api_key: str = None):
  api_response = await api_request("POST", f"/admin/devices/{device_id}/deactivate", "", None, api_key)
  return api_response