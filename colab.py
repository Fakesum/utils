# Only for running on google colab
def install():
    !apt-get update
    !apt install chromium-chromedriver xvfb
    !wget https://github.com/korakot/kora/releases/download/v0.10/py310.sh
    !bash ./py310.sh -b -f -p /usr/local
    !python -m ipykernel install --name "py310" --user
    !python -m pip install undetected-chromedriver PyVirtualDisplay loguru