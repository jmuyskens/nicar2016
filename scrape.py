#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import unicodecsv
import requests
from dateutil.parser import parse
from bs4 import BeautifulSoup

url = "http://www.ire.org/conferences/nicar2016/schedule/"
fieldnames = ["title", "speaker", "description", "room", "day", "start_time", "end_time"]

def parse_session(session, day):
	'''
	given an session html title_block representing a session
	return a dictionary of data about the session
	'''
	session_data = {}

	session_data["day"] = str(day)
	date = datetime(2016, 3, 9 + day)

	category = session.find("div", class_="heading5").text
	title_block = session.find("div", class_="col-60 body2 gray-45")
	session_data["title"] = title_block.find("h3").find("a").text
	session_data["speaker"] = title_block.find_all("p")[0].text.replace("Speaker: ", "").replace("Speakers: ", "")
	session_data["description"] = ""
	if len(title_block.find_all("p")) > 1:
		session_data["description"] = title_block.find_all("p")[1].text
	meta_block = session.find("div", class_="meta")
	session_data["room"] = meta_block.find_all("p")[0].text
	time = meta_block.find_all("p")[1].text
	start_time, end_time = time.split(" - ")
	session_data["start_time"] = parse(start_time, default=date).isoformat()
	session_data["end_time"] = parse(end_time, default=date).isoformat()

	return session_data

def to_csv(data, props):
	return ",".join(['"{}"'.format(data[prop].encode("utf8", "replace")) for prop in props])

r = requests.get(url)
soup = BeautifulSoup(r.text, "html.parser")
article = soup.find("article", class_="main-content-item")
panes = article.find_all("ul", class_="listview pane")

session_data_list = []
for i, pane in enumerate(panes):
	sessions = pane.find_all('li')
	session_data_list.extend(
		[parse_session(session, i) for session in sessions])

with open('nicar.csv', 'w') as f:
	writer = unicodecsv.DictWriter(f, fieldnames)
	writer.writeheader()
	writer.writerows(session_data_list)


