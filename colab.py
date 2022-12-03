# Only for running on google colab
def install():
    !pip install undetected_chromedriver PyVirtualDisplay
    !apt update
    !apt install xvfb chromium-chromedriver