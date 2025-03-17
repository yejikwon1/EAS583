import requests
import json

PINATA_API_KEY="3294fa2ac3a8b5454d5c"
PINATA_SECRET_API_KEY="6fce643db98dd2c09352b9eef212e48ebee7575cc69823be978e24a57bbf9cd6"
PINATA_PIN_JSON_URL="https://api.pinata.cloud/pinning/pinJSONToIPFS"


IPFS_GATEWAY= "https://gateway.pinata.cloud/ipfs/"

def pin_to_ipfs(data):

	headers={
		"Content-Type":"application/json",
		"pinata_api_key":PINATA_API_KEY,
		"pinata_secret_api_key":PINATA_SECRET_API_KEY,	
	}

	json_data={
		"pinataContent":data,
		"pinataMetadata":{"name":"my_json_data"}
	}

	response=requests.post(PINATA_PIN_JSON_URL,headers=headers,json=json_data)

	if response.status_code==200:
		cid=response.json()["IpfsHash"]
		return cid

	else:
		return None

	#assert isinstance(data,dict), f"Error pin_to_ipfs expects a dictionary"
	#YOUR CODE HERE



def get_from_ipfs(cid,content_type="json"):
	assert isinstance(cid,str), "get_from_ipfs accepts a cid in the form of a string"
	#YOUR CODE HERE	

	url=f"{IPFS_GATEWAY}{cid}"
	response=requests.get(url)

	if response.ok:
		try:
			return response.json()
		except requests.exceptions.JSONDecodeError:
			return response.text
	raise Exception(f"failed")
