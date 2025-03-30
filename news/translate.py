# ruff: noqa: S314, E501, UP031
import re
from pathlib import Path
from xml.etree import ElementTree as ET

import requests

base_language = "it"


def secret(path):
    if secret.cached.get(path, "") == "":
        with Path(path).open() as secret_file:
            encoded_secret = secret_file.read()
        secret.cached[path] = encoded_secret
    return secret.cached[path]


secret.cached = {}


class TranslationError(Exception):
    """Custom exception for translation errors."""


def get_token():
    # Get the access token from ADM, token is good for 10 minutes
    key = secret("secrets/key")
    url = f"https://api.cognitive.microsoft.com/sts/v1.0/issueToken?Subscription-Key={key}"
    access_token = requests.post(url, data="", timeout=5)
    if access_token.status_code == 200:  # noqa: PLR2004
        token = "Bearer " + access_token.text
    else:
        message = f"error while getting token ! status code = {access_token.status_code}, status message = {access_token.text}"
        raise TranslationError(message)
    return token


def translate(token, from_lang_code, title, content):
    title_translated = ""
    content_translated = ""
    split = split_content(content, 8000)
    for s in split:
        xml = """<?xml version="1.0"?>
            <TranslateArrayRequest>
                <AppId/>
                <From>%s</From>
                <Options>
                    <Category xmlns="http://schemas.datacontract.org/2004/07/Microsoft.MT.Web.Service.V2" />
                    <ContentType xmlns="http://schemas.datacontract.org/2004/07/Microsoft.MT.Web.Service.V2">text/html</ContentType>
                    <ReservedFlags xmlns="http://schemas.datacontract.org/2004/07/Microsoft.MT.Web.Service.V2" />
                    <State xmlns="http://schemas.datacontract.org/2004/07/Microsoft.MT.Web.Service.V2" />
                    <Uri xmlns="http://schemas.datacontract.org/2004/07/Microsoft.MT.Web.Service.V2" />
                    <User xmlns="http://schemas.datacontract.org/2004/07/Microsoft.MT.Web.Service.V2" />
                </Options>
                <Texts>
                    <string xmlns="http://schemas.microsoft.com/2003/10/Serialization/Arrays"><![CDATA[%s]]></string>
                    <string xmlns="http://schemas.microsoft.com/2003/10/Serialization/Arrays"><![CDATA[%s]]></string>
                </Texts>
                <To>%s</To>
            </TranslateArrayRequest>""" % (
            from_lang_code,
            title,
            s,
            base_language,
        )
        headers = {
            "Authorization ": token,
            "Content-Type": "application/xml; charset=utf-8",
        }
        url = "http://api.microsofttranslator.com/v2/Http.svc/TranslateArray"
        translation_data = requests.post(
            url,
            headers=headers,
            data=xml.encode("utf-8"),
            timeout=30,
        )  # make request
        if translation_data.status_code == 200:  # noqa: PLR2004
            translation = ET.fromstring(
                translation_data.text.encode("utf-8"),
            )  # parse xml return values
            title_translated = translation[0][3].text
            if len(translation) > 1:
                if translation[1][3].text:
                    content_translated += translation[1][3].text
        else:
            message = f"error ! status code = {translation_data.status_code}, status message = {translation_data.text}"
            raise TranslationError(message)
    return (title_translated, content_translated)


def split_content(content, max_length):
    # splits the content in an array of strings
    # with length approximately less than or equal to max_length
    # taking care not to break up the tags
    open_tag = re.compile(r"<")
    close_tag = re.compile(r">")
    split = []
    while True:
        s = content[:max_length]
        content = content[max_length:]
        o = len(open_tag.findall(s))
        c = len(close_tag.findall(s))
        if o > c:
            pos = content.find(">")
            if pos >= 0:
                s = s + content[: pos + 1]
                content = content[pos + 1 :]
        if o < c:
            pos = s.rfind(">")
            if pos >= 0:
                s = s[: pos - 1]
                content = s[pos - 1 :] + content
        split.append(s)
        if len(content) == 0:
            break
    return split
