# localpilot

! This is a fork of [danielgross](https://github.com/danielgross)'s [localpilot](https://github.com/danielgross/localpilot) implementation with addition of supporting Remote OpenAI Compatible APIs and the bypass for auth for the Copilot and Copilot Chat extensions. !

_Use GitHub Copilot and Copilot Chat locally on your Macbook with one-click!_

![image](https://github.com/danielgross/localpilot/assets/279531/521d0613-7423-4839-a5e8-42098cd65a5e)

## Demo Video

https://github.com/danielgross/localpilot/assets/279531/3259981b-39f7-4bfa-8a45-84bde6d4ba4c

_This video is not sped up or slowed down._

## Installation

1. First, open VS Code Settings and add the following to your settings.json file:

```json
"github.copilot.advanced": {
    "debug.testOverrideProxyUrl": "http://localhost:5001",
    "debug.overrideProxyUrl": "http://localhost:5001",
    "debug.chatOverrideProxyUrl" : "http://localhost:5001",
}
```

2. Bypass auth for Copilot and Copilot Chat extensions

   - replace `{base:n,api:s}` with `{ base: Kc.URI.parse('http://localhost:5001', !0), api: Kc.URI.parse('http://localhost:5001', !0) }` in extension.js of copilot (found in `~/.vscode/extensions/github.copilot-1.143.0/dist/extension.js`)
   - replace `` `${this.baseUri.scheme}://api.${this.baseUri.authority}` `` with `'http://localhost:5001'` in extension.js of copilot chat (found in `~/.vscode/extensions/github.copilot-chat-0.11.1/dist/extension.js`)

3. Configure more models

You can add new models, with these formats to the list `models` in `config.py`:

    - For a model to be downloaded and served in the same machine:

```python
    "Mistral-7b": {
        "url": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q5_K_M.gguf",
        "type": "local",
        "filename": "mistral-7b-instruct-v0.1.Q5_K_M.gguf",
    },
```

    - For using a hosted OpenAI compatible API without auth :

```python
    "Zephyr": {
        "domain": "http://someurl:8000",
        "model": "zephyr-7b-beta.Q4_0",
        "type": "remote",
    },
```

    - For using a hosted OpenAI compatible API with auth :

```python
    "Mistral": {
        "domain": "http://someurl:8000",
        "model": "mistral-7b-code-16k-qlora.Q6_K",
        "api_key": "SOME_API_KEY",
        "type": "remote",
    },
```

4. Create a virtualenv to run this Python process, install the requirements, and download the models.

```python
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
# First setup run. This will download several models to your ~/models folder. ( you can skip this step if you only plan on using remotely hosted models)
python app.py --setup
```

5. Choose a model in the ModelPicker

![image](https://github.com/danielgross/localpilot/assets/279531/521d0613-7423-4839-a5e8-42098cd65a5e)

6. Run it!

```python
python app.py
```

7. Reload your VSCode windows to apply the changes in the Copilot extensions

Enjoy your on-device Copilot!


NB:
if you want to disable Telemetry, you can replace all of these in both extension.js:
`"https://copilot-telemetry.githubusercontent.com/telemetry"` with `"http://localhost:5001/telemetry"`
`"https://default.exp-tas.com` with `"http://localhost:5001/telemetry`
`"https://origin-tracker.githubusercontent.com"` with `"http://localhost:5001/telemetry"`

However, this may violate Copilot's Terms of Service, so proceed at your own risk.

## Caveat FAQ

**Is the code as good as GitHub Copilot?**

For simple line completions yes. For simple function completions, mostly. For complex functions... maybe.

**Is it as fast as GitHub Copilot?**

On my Macbook Pro with an Apple M2 Max, the 7b models are roughly as fast. The 34b models are not. Please consider this repo a demonstration of a very inefficient implementation. I'm sure we can make it faster; please do submit a pull request if you'd like to help. For example, I think we need debouncer because sometimes llama.cpp/GGML isn't fast at interrupting itself when a newer request comes in.

**Can this be packaged as a simple Mac app?**

Yes!, I'm sure it can be, I just haven't had the time. Please do submit a pull request if you're into that sort of thing!

**Should there be a meta-model that routes to a 1b for autocomplete, 7b for more complex autocomplete, and a 34b for program completion?**

Hmm, that seems like an interesting idea.

**OK, but in summary, is it good?**

Only if your network is bad. I don't think it's competitive if you have fast Internet. But it sure is awesome on airplanes and while tethering!
