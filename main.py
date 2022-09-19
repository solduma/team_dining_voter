import streamlit as st
import json
from pytimekr import pytimekr
from datetime import datetime, timedelta
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc
import random
rc('font', family='AppleGothic')
plt.rcParams['axes.unicode_minus'] = False

def read_data(filename):
  f = open('data/' + filename)
  output = json.load(f)
  f.close()
  return output


def save_data(dictionary, filename):
  json_object = json.dumps(dictionary, indent=4)
  with open('data/' + filename + '.json', "w") as outfile:
    outfile.write(json_object)


def list_dates(start, end):
  dates = []
  holidays = pytimekr.holidays(start.year)
  if start.year != end.year:
    holidays = holidays + pytimekr.holidays(int(end.year))
  delta = end - start
  for i in range(delta.days + 1):
    day = (start + timedelta(days=i)).date()
    if (day not in holidays) and day.weekday() < 5:
      dates.append(day)
  return sorted(
    [date.strftime('%Y-%m-%d') + ' 점심' for date in dates] + [date.strftime('%Y-%m-%d') + ' 저녁' for date in dates])

def reset_json(filename):
  dictionary = {
    "registered": False,
    "unavail_dates": [
    ],
    "locations": [
    ],
    "voted": False,
    "voted_dates": [
    ],
    "voted_locations": [
    ]
  }
  save_data(dictionary, filename)

def reset_all():
  for f in os.listdir("data"):
    if f != 'admin.json':
      reset_json(f.split('.')[0])


data = read_data('admin.json')
p_data = {}
for f in os.listdir("data"):
  if f != 'admin.json':
    p_data[f.split('.')[0]] = read_data(f)

is_name_selected = False

st.title('회식 투표기')

tab1, tab2, tab3, tab4 = st.tabs(["회식 불가일 및 추천 장소 등록", "일자 투표", "장소 투표", "결과"])

with tab1:
  name = st.selectbox(
    '이름을 입력하세요',
    ('-- 선택 --', '이한주', '조란', '이선화', '유일조', '조인준', '김소희'))
  if name == '-- 선택 --':
    st.write('이름을 선택해 주세요')
  else:
    st.success(name + '님 환영합니다')
    is_name_selected = True
    if is_name_selected:
      p_datum = p_data[name]

      start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
      end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
      unavail_dates = p_datum['unavail_dates']

      if st.button("리셋"):
        reset_json(name)


      options = st.multiselect(
        data['start_date'] + " - " + data['end_date'] + " 사이의 기간 중 불가능한 날짜를 등록 해 주세요",
        list_dates(start_date, end_date),
        unavail_dates)

    if st.button("등록", "등록1"):
      p_datum["unavail_dates"] = options
      p_datum["registered"] = True
      save_data(p_datum, name)
      st.success('등록 완료!')

    if is_name_selected:
      place = st.text_input('장소를 등록 해 주세요', '')
      container = st.empty()
      container.markdown('현재 등록된 장소:' + ", ".join(
        list(dict.fromkeys([item for sublist in [p_data[p]['locations'] for p in p_data] for item in sublist]))))

    if st.button("등록", "등록2"):
      if place != '':
        p_datum["locations"] = p_datum["locations"] + [place]
        p_datum["registered"] = True
        save_data(p_datum, name)
        container.write('현재 등록된 장소:' + ", ".join(
            list(dict.fromkeys([item for sublist in [p_data[p]['locations'] for p in p_data] for item in sublist]))))
        st.success('등록 완료!')

with tab2:
  if is_name_selected:
    unavail_dates_all = [item for sublist in [p_data[p]['unavail_dates'] for p in p_data] for item in sublist]
    all_dates = dict.fromkeys(list_dates(start_date, end_date), 0)
    for d in unavail_dates_all:
      if d:
        all_dates[d] += 1
    sorted_dates = dict(sorted(all_dates.items(), key=lambda item: item[1]))

    del unavail_dates_all
    del all_dates

    checkboxes_dates = [st.checkbox(x + " - 참석 불가 인원: " + str(sorted_dates[x]) + "명") for x in sorted_dates]

    voted_dates = []
    if st.button("투표", "투표1"):
      for i in range(len(sorted_dates)):
        if checkboxes_dates[i]:
          voted_dates.append(list(sorted_dates.items())[i][0])
      p_datum["voted_dates"] = voted_dates
      p_datum["voted"] = True
      save_data(p_datum, name)
      st.success('투표 완료!')

with tab3:
  if is_name_selected:
    places = list(dict.fromkeys([item for sublist in [p_data[p]['locations'] for p in p_data] for item in sublist]))
    checkboxes_places = [st.checkbox(x) for x in places]

    voted_locations = []
    if st.button("투표", "투표2"):
      for i in range(len(places)):
        if checkboxes_places[i]:
          voted_locations.append(places[i])
      p_datum["voted_locations"] = voted_locations
      p_datum["voted"] = True
      save_data(p_datum, name)
      st.success('투표 완료!')

with tab4:
  finalist_locations = [item for sublist in [p_data[p]['voted_locations'] for p in p_data] for item in sublist]
  final_locations = {}

  for l in finalist_locations:
    if l in final_locations:
      final_locations[l] = final_locations[l] + 1
    else:
      final_locations[l] = 1

  df = pd.DataFrame.from_dict(final_locations, orient='index', columns=['득표'])
  st.dataframe(df)
  st.bar_chart(df)

  mylabels = df.index
  fig, ax = plt.subplots()
  ax.pie(df['득표'], labels= mylabels, autopct='%1.1f%%', startangle=90)

  st.pyplot(fig)
  if st.button('투표'):
    st.write("'" + random.choice(finalist_locations) + "' 으로 선정 되었습니다")