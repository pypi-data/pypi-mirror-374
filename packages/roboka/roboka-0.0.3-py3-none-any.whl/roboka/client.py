import requests
import json
import time

now = time.time()

class Update:
    def __init__(self, message_data, chat_id, client):
        self.text = message_data.get("text", "")
        self.message_id = message_data.get("message_id", None)
        self.sender_id = message_data.get("sender_id", None)
        self.chat_id = chat_id
        self.raw = message_data
        self._client = client

    def reply(self, text: str):
        url = f"https://botapi.rubika.ir/v3/{self._client.token}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": text,
            "reply_to_message_id": self.message_id
        }

        resp = requests.post(url, json=data)
        jsn = resp.json()
        if resp.status_code == 200:
            if jsn.get("status") != "OK":
                return resp.text
            return jsn
        return resp.text

class Client:
	
	def __init__(
		self, 
		token:str
	):
		self.token = token
		self.url = f"https://botapi.rubika.ir/v3/{self.token}/getMe"
		self.response = requests.post(self.url)
		self.jsn = self.response.json()
		if self.response.status_code == 200:
			if self.jsn["status"] != "INVALID_ACCESS":
				self.username = self.jsn["data"]["bot"]["username"]
				print(f"You have successfully logged in to the @{self.username} bot.\n")
				print("This library was created by the channel @roboka_library")
			else:
				return self.response.text
		else:
			return self.response.text
			
	def send_text(
		self,  
		chat_id:str,
		text:str,
		message_id:str=None
	):
		self.chat_id = chat_id
		self.text = text
		self.message_id = message_id
		self.url = f"https://botapi.rubika.ir/v3/{self.token}/sendMessage"
		self.data = {
	    	"chat_id": self.chat_id,
			"text": self.text
		}
		if self.message_id != None:
			self.data = {
			    "chat_id": self.chat_id,
			    "text": self.text,
			    "reply_to_message_id": self.message_id
			}
		self.response = requests.post(self.url, json=self.data)
		self.jsn = self.response.json()
		if self.response.status_code == 200:
			if self.jsn["status"] != "OK":
				return self.response.text
			else:
				return self.jsn	
		else:
			return self.response.text
			
	def get_me(self):
		self.url = f"https://botapi.rubika.ir/v3/{self.token}/getMe"
		self.response = requests.post(self.url)
		self.jsn = self.response.json()
		if self.response.status_code == 200:
			if self.jsn["status"] != "INVALID_ACCESS":
				return self.jsn
			else:
				return self.response.text
		else:
			return self.response.text
	
	def on_message(self, limit=100):
	    url = f'https://botapi.rubika.ir/v3/{self.token}/getUpdates'
	    offset_id = None
	    last_message_id = None
	    

	    while True:
	        try:
	            data = {"limit": limit}
	            if offset_id:
	                data["offset_id"] = offset_id

	            response = requests.post(url, json=data, timeout=5)
	            response.raise_for_status()
	            result = response.json()
	            updates = result["data"]["updates"]
	            of = result["data"]["next_offset_id"]
	            offset_id = of
	            if updates:
	                last_update = updates[-1]
	                offset_id = result["data"].get("next_offset_id")
	                new_msg = last_update.get("new_message", {})
	                chat_id = last_update.get("chat_id")
	                message_id = new_msg.get("message_id")
	                tim = new_msg["time"]
	                if int(tim) >= now:
		                if message_id != last_message_id:
		                    last_message_id = message_id
		                    yield Update(new_msg, chat_id, client=self)

	        except requests.exceptions.RequestException as e:
	            print("❗ خطای ارتباط:", e)
	            continue

	        except (KeyError, ValueError) as e:
	            continue

	        except Exception as e:
	            print("❗ خطای ناشناخته:", e)
	            continue

	        time.sleep(0.1)
	        
	def create_keypad(
		self,
		chat_id:str,
		text:str,
		rows:list,
		message_id:str=None
	):
		self.chat_id = chat_id
		self.text = text
		self.rows = rows
		self.message_id = message_id
		self.data = {
			"chat_id": self.chat_id,
		    "text": self.text,
		    "chat_keypad_type": "New",
		    "chat_keypad": {
		        "rows": self.rows,
		        "resize_keyboard": True,
		        "on_time_keyboard": False
		    }
		}
		if self.message_id != None:
			self.data = {
				"chat_id": self.chat_id,
			    "text": self.text,
			    "chat_keypad_type": "New",
			    "reply_to_message_id": self.message_id,
			    "chat_keypad": {
			        "rows": self.rows,
			        "resize_keyboard": True,
			        "on_time_keyboard": False
			    }
			}
		self.headers = {
		    'Content-Type': 'application/json'
		}
		self.url = f'https://botapi.rubika.ir/v3/{self.token}/sendMessage'
		self.response = requests.post(self.url, headers=self.headers, json=self.data)
		self.jsn = self.response.json()
		return self.jsn

	def send_poll(
		self,
		chat_id:str,
		question:str,
		options:list
	):
		self.chat_id = chat_id
		self.question = question
		self.options = options
		self.data = {
		    "chat_id": self.chat_id,
		    "question": self.question,
		    "options": self.options,
		}
		self.url = f'https://botapi.rubika.ir/v3/{self.token}/sendPoll'
		self.response = requests.post(self.url, json=self.data)
		self.jsn = self.response.json()
		return self.jsn

	def send_location(
		self,
		chat_id:str,
		latitude:int,
		longitude:int,
		message_id:str=None
	):
		self.chat_id = chat_id
		self.latitude = latitude
		self.longitude = longitude
		self.message_id = message_id
		self.data = {
		    "chat_id": self.chat_id,
		    "latitude": self.latitude,
		    "longitude": self.longitude
		}
		if self.message_id != None:
			self.data = {
			    "chat_id": self.chat_id,
			    "latitude": self.latitude,
			    "longitude": self.longitude,
			    "reply_to_message_id": self.message_id
			}
		self.url = f'https://botapi.rubika.ir/v3/{self.token}/sendLocation'
		self.response = requests.post(self.url, json=self.data)
		self.jsn = self.response.json()
		return self.jsn

	def edit_text(
		self,
		chat_id:str,
		text:str,
		message_id:int
	):
		self.chat_id = chat_id
		self.text = text
		self.message_id = message_id
		self.data = {
		    "chat_id": self.chat_id,
		    "message_id": self.message_id,
		    "text": self.text
		}
		self.url = f'https://botapi.rubika.ir/v3/{self.token}/editMessageText'
		self.response = requests.post(self.url, json=self.data)
		self.jsn = self.response.json()
		return self.jsn

	def send_contact(
		self,
		chat_id:str,
		first_name:str,
		last_name:str,
		phone_number:int,
		message_id:int=None
	):
		self.chat_id = chat_id
		self.first_name = first_name
		self.last_name = last_name
		self.phone_number = phone_number
		self.message_id = message_id
		self.data = {
		    "chat_id": self.chat_id,
		    "first_name": self.first_name,
		    "last_name": self.last_name,
		    "phone_number": self.phone_number
		}
		if self.message_id != None:
			self.data = {
		    "chat_id": self.chat_id,
		    "first_name": self.first_name,
		    "last_name": self.last_name,
		    "phone_number": self.phone_number,
		    "reply_to_message_id": self.message_id
		}
		self.url = f'https://botapi.rubika.ir/v3/{self.token}/sendContact'
		self.response = requests.post(self.url, json=self.data)
		self.jsn = self.response.json()
		return self.jsn

	def get_chat(
		self,
		chat_id:str
	):
		self.chat_id = chat_id
		self.data = {
			"chat_id": self.chat_id
		}
		self.url = f'https://botapi.rubika.ir/v3/{self.token}/getChat'
		self.response = requests.post(self.url, json=self.data)
		self.jsn = self.response.json()
		return self.jsn

	def forward_message(
		self,
		from_chat_id:str,
		message_id:int,
		to_chat_id:str
	):
		self.from_chat_id = from_chat_id
		self.message_id = message_id
		self.to_chat_id = to_chat_id
		self.data = {
		    "from_chat_id": self.from_chat_id,
		    "message_id": self.message_id,
		    "to_chat_id": self.to_chat_id
		}
		self.url = f'https://botapi.rubika.ir/v3/{self.token}/forwardMessage'
		self.response = requests.post(self.url, json=self.data)
		self.jsn = self.response.json()
		return self.jsn

	def delete_message(
		self,
		chat_id:str,
		message_id:int
	):
		self.chat_id = chat_id
		self.message_id = message_id
		self.data = {
		    "chat_id": self.chat_id,
		    "message_id": self.message_id
		}
		self.url = f'https://botapi.rubika.ir/v3/{self.token}/deleteMessage'
		self.response = requests.post(self.url, json=self.data)
		self.jsn = self.response.json()
		return self.jsn

	def create_inline_keypad(
		self,
		chat_id:str,
		text:str,
		rows:list,
		message_id:str=None
	):
		self.chat_id = chat_id
		self.text = text
		self.rows = rows
		self.message_id = message_id
		self.data = {
			"chat_id": self.chat_id,
		    "text": self.text,
		    "inline_keypad": {
		        "rows": self.rows,
		    }
		}
		if self.message_id != None:
			self.data = {
				"chat_id": self.chat_id,
			    "text": self.text,
			    "reply_to_message_id": self.message_id,
			    "inline_keypad": {
			        "rows": self.rows,
			    }
			}
		self.headers = {
		    'Content-Type': 'application/json'
		}
		self.url = f'https://botapi.rubika.ir/v3/{self.token}/sendMessage'
		self.response = requests.post(self.url, headers=self.headers, json=self.data)
		self.jsn = self.response.json()
		return self.jsn

	def get_upload_url(
		self,
		type:str
	):
		self.type = type
		self.data = {
			"type": self.type
		}
		self.url = f'https://botapi.rubika.ir/v3/{self.token}/requestSendFile'
		response = requests.post(self.url, json=self.data)
		return response.json()["data"]["upload_url"]

	def get_file_id(self, url: str, file_name: str, file_path: str) -> str:
	    with open(file_path, "rb") as f:
	        files = {
	            "file": (file_name, f, "application/octet-stream")
	        }
	        response = requests.post(url, files=files, verify=False)
	        response.raise_for_status()
	
	        data = response.json()
	        return data["data"]["file_id"]
	
	def send_file(
		self,
		chat_id:str,
		text:str,
		file_name:str,
		file_path:str,
		file_type:str,
		message_id:str=None
	):
		self.chat_id = chat_id
		self.text = text
		self.message_id = message_id
		self.file_name = file_name
		self.file_path = file_path
		self.file_type = file_type
		self.upload_url = self.get_upload_url(self.file_type)
		self.file_id = self.get_file_id(self.upload_url, self.file_name, self.file_path)
		self.data = {
		    "chat_id": self.chat_id,
		    "file_id": self.file_id,
		    "text": self.text
		}
		if self.message_id != None:
			self.data = {
		    "chat_id": self.chat_id,
		    "file_id": self.file_id,
		    "text": self.text,
		    "reply_to_message_id": self.message_id
			}
		self.url = f'https://botapi.rubika.ir/v3/{self.token}/sendFile'
		self.response = requests.post(self.url, json=self.data)
		self.jsn = self.response.json()
		return self.jsn

	def send_image(
		self,
		chat_id:str,
		text:str,
		file_name:str,
		file_path:str,
		message_id:str=None
	):
		self.chat_id = chat_id
		self.text = text
		self.message_id = message_id
		self.file_name = file_name
		self.file_path = file_path
		self.upload_url = self.get_upload_url("Image")
		self.file_id = self.get_file_id(self.upload_url, self.file_name, self.file_path)
		self.data = {
		    "chat_id": self.chat_id,
		    "file_id": self.file_id,
		    "text": self.text
		}
		if self.message_id != None:
			self.data = {
		    "chat_id": self.chat_id,
		    "file_id": self.file_id,
		    "text": self.text,
		    "reply_to_message_id": self.message_id
			}
		self.url = f'https://botapi.rubika.ir/v3/{self.token}/sendFile'
		self.response = requests.post(self.url, json=self.data)
		self.jsn = self.response.json()
		return self.jsn

	def send_video(
		self,
		chat_id:str,
		text:str,
		file_name:str,
		file_path:str,
		message_id:str=None
	):
		self.chat_id = chat_id
		self.text = text
		self.message_id = message_id
		self.file_name = file_name
		self.file_path = file_path
		self.upload_url = self.get_upload_url("Video")
		self.file_id = self.get_file_id(self.upload_url, self.file_name, self.file_path)
		self.data = {
		    "chat_id": self.chat_id,
		    "file_id": self.file_id,
		    "text": self.text
		}
		if self.message_id != None:
			self.data = {
		    "chat_id": self.chat_id,
		    "file_id": self.file_id,
		    "text": self.text,
		    "reply_to_message_id": self.message_id
			}
		self.url = f'https://botapi.rubika.ir/v3/{self.token}/sendFile'
		self.response = requests.post(self.url, json=self.data)
		self.jsn = self.response.json()
		return self.jsn

	def get_updates(
		self,
		limit:str,
		offset_id:str=None
	):
		self.limit = limit
		self.offset_id = offset_id
		self.data = {
		    "limit": self.limit,
		}
		if self.offset_id != None:
			self.data = {
		        "limit": self.limit,
		        "offset_id": self.offset_id
			}
		self.url = f'https://botapi.rubika.ir/v3/{self.token}/getUpdates'
		self.response = requests.post(self.url, json=self.data)
		self.jsn = self.response.json()
		return self.jsn

	def edit_keypad(
		self,
		chat_id:str,
		rows:list,
	):
		self.chat_id = chat_id
		self.rows = rows
		self.data = {
			"chat_id": self.chat_id,
		    "chat_keypad_type": "New",
		    "chat_keypad": {
		        "rows": self.rows,
		        "resize_keyboard": True,
		        "on_time_keyboard": False
		    }
		}
		self.headers = {
		    'Content-Type': 'application/json'
		}
		self.url = f'https://botapi.rubika.ir/v3/{self.token}/editChatKeypad'
		self.response = requests.post(self.url, headers=self.headers, json=self.data)
		self.jsn = self.response.json()
		return self.jsn

	def set_commands(
		self,
		commands:list,
	):
		self.commands = commands
		self.data = {
		    "bot_commands": self.commands,
		}
		self.url = f'https://botapi.rubika.ir/v3/{self.token}/setCommands'
		self.response = requests.post(self.url, json=self.data)
		self.jsn = self.response.json()
		return self.jsn

	def set_webhook(
		self,
		url:str,
		type:str
	):
		self.wburl = url
		self.type = type
		self.data = {
		    "url": self.wburl,
		    "type": self.type
		}
		self.url = f'https://botapi.rubika.ir/v3/{self.token}/updateBotEndpoints'
		self.response = requests.post(self.url, json=self.data)
		self.jsn = self.response.json()
		return self.jsn