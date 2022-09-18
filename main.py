import streamlit as st
import json
from pytimekr import pytimekr
from datetime import datetime, timedelta
import os

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


data = read_data('admin.json')
p_data = {}
for f in os.listdir("data"):
    if f != 'admin.json':
        p_data[f.split('.')[0]] = read_data(f)

is_name_selected = False

st.title('회식 투표기')

tab1, tab2, tab3 = st.tabs(["회식 불가일 및 추천 장소 등록", "투표", "결과"])

with tab1:
    name = st.selectbox(
        '이름을 입력하세요',
        ('-- 선택 --', '이한주', '조란', '이선화', '유일조', '조인준', '김소희'))
    if name == '-- 선택 --':
        st.write('이름을 선택해 주세요')
    else:
        st.write(name + '님 환영합니다')
        is_name_selected = True
        if is_name_selected:
            p_datum = p_data[name]

            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
            unavail_dates = p_datum['unavail_dates']

            options = st.multiselect(
                data['start_date'] + " - " + data['end_date'] + " 사이의 기간 중 불가능한 날짜를 등록 해 주세요",
                list_dates(start_date, end_date),
                unavail_dates)

        if st.button("등록", "등록1"):
            p_datum["unavail_dates"] = options
            p_datum["registered"] = True
            save_data(p_datum, name)
            st.write('등록 완료!')

        if is_name_selected:
            place = st.text_input('장소를 등록 해 주세요', '')
            st.write('현재 등록된 장소:', ", ".join(list(dict.fromkeys([item for sublist in [p_data[p]['locations'] for p in p_data] for item in sublist]))))

        if st.button("등록", "등록2"):
            p_datum["locations"] = p_datum["locations"] + [place]
            p_datum["registered"] = True
            save_data(p_datum, name)
            st.write('등록 완료!')

with tab2:
    st.write('감사합니다')


with tab3:
    st.write('감사합니다')
