# DeepSeek'r

Selenium DeepSeek automation library for Python.

## Why "just another wrapper library"?

I know there are some similar libraries already, but the reasons I’m releasing this one are:
- Most of the ones I found were outdated or not working.
- I’m working on another project and this was the script I needed. So I decided to release DeepSeek'r separately.

# Credits / Thanks

- The most up-to-date DeepSeek Selenium automation script I found was [NewComer00/deepseek-chatbot](https://github.com/NewComer00/deepseek-chatbot). DeepSeek'r is partly based on it.
- Why did I make DeepSeek'r based on it, then?
	- [NewComer00/deepseek-chatbot](https://github.com/NewComer00/deepseek-chatbot) uses Edge, but I needed Chrome for my project. So DeepSeek'r uses Google Chrome. (DeepSeek'r also includes other small changes and improvements.)

# Example Usage

1. Install DeepSeek'r  
	```bash
	pip install deepseekr
	```

2. Basic Usage  
	```python
	from deepseekr import DeepSeek

	# minimal
	ds1 = DeepSeek()
	print(ds1.send_prompt("Hi"))
	ds1.close()

	# with headless (BETA - may not work on some devices!)
	ds2 = DeepSeek(headless=True)
	print(ds2.send_prompt("Running in headless mode"))
	ds2.close()

	# with custom profile path (saves cookies there, so you don’t have to log in again)
	ds3 = DeepSeek(profile_path="my_profile")
	print(ds3.send_prompt("Using custom profile path"))
	ds3.close()

	# with session name (BETA)
	ds4 = DeepSeek(session_name="Work Chat")
	print(ds4.send_prompt("Resuming session Work Chat"))
	ds4.close()

	# with Chrome binary path
	ds5 = DeepSeek(chrome_path="/Applications/Chrome.app/Contents/MacOS/Google Chrome")
	print(ds5.send_prompt("Using custom Chrome path"))
	ds5.close()
	```

# Notes

Currently, DeepSeek'r is developed and tested only on macOS. It *may be incompatible with other operating systems!*

# Versions
- [0.1.0](https://pypi.org/project/deepseekr/0.1.0/): First version
- [0.2.0](https://pypi.org/project/deepseekr/0.2.0/): Important! DeepSeek's UI on its website just got updated / changed. This update adds support for it. Older versions does not work anymore!
- [0.3.0](https://pypi.org/project/deepseekr/0.3.0/): Added "server busy" handling.

If you are already using DeepSeek'r on your projects, please update it using:
`pip install -U deepseekr`

# Disclaimer

This repository is **only for research purposes**. I am not responsible for misuse, as this works like a *free and unlimited DeepSeek API*. Please do not use in production!

# Contact & Support

📧 [yusuf@tachion.tech](mailto:yusuf@tachion.tech)  
☕ [Buy me a coffee](https://buymeacoffee.com/myusuf)

Thanks — hope this helps!
