import numpy as np
import pandas as pd
import scipy
import streamlit as st
import matplotlib.pyplot as plt

st.title("Контроль групп риска")
st.subheader('Загрузите файл')
upload_file = st.file_uploader('Выберите файл')
if uploaded_file is not None:
    df = pd.read_csv(upload_file, encoding='cp1251')

def min_max_days(df):
    min_days = int(df['Количество больничных дней'].min())
    max_days = int(df['Количество больничных дней'].max())
    return min_days, max_days


# диапазоны значений возрастов
def min_max_age(df):
    min_age = int(df['Возраст'].min())
    max_age = int(df['Возраст'].max())
    return min_age, max_age


# деленеие на выборки для сравнения по полу и проведение стат.теста
def male_female_hipo(df, work_days):
    df = df.loc[df['Количество больничных дней'] >= work_days]
    males = df.loc[df['Пол'] == 'М', 'Количество больничных дней']
    females = df.loc[df['Пол'] == 'Ж', 'Количество больничных дней']
    return males, females


# делание на выборки для сравнения по возрвсту и проведение стат.теста
def age_hipo(df, age, min_age):
    above = df.loc[df['Возраст'] >= age]
    below = df.loc[df['Возраст'].between(min_age, age)]
    above_1 = above[above['Количество больничных дней'] != 0]
    below_1 = below[below['Количество больничных дней'] != 0]
    max_day = int(max(
        list(above_1['Количество больничных дней'].unique()) + list(below_1['Количество больничных дней'].unique())))
    min_day = int(min(
        list(above_1['Количество больничных дней'].unique()) + list(below_1['Количество больничных дней'].unique())))
    return above, below, max_day, min_day


def statistic(sample_1, sample_2):
    stat, p = scipy.stats.mannwhitneyu(sample_1, sample_2)
    return p


app_mode = st.sidebar.selectbox('Группы риска', ['Разделение по полу', 'Разделение по возрасту'])

if app_mode == 'Разделение по полу':
    # выбор порога пропущенных дней
    min_days, max_days = min_max_days(df)
    st.markdown(':red[Выберите порог пропущенных дней]')
    work_days = st.slider('work_days', min_days, max_days)
    st.markdown(
        f'_Требуется проверить гипотезу, что мужчины пропускают в течение года более {work_days} рабочих дней по болезни значимо чаще женщин_')
    males, females = male_female_hipo(df, work_days)
    p = statistic(males, females)
    # распределения по выборкам
    fig = plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.title('Мужчины')
    plt.hist(np.array(males), bins=4)
    plt.subplot(1, 2, 2)
    plt.title('Женщины')
    plt.hist(np.array(females), bins=4)
    fig.suptitle('Распределение пропущенных дней для мужчин и женщин')
    st.pyplot(fig)

    st.markdown(
        'Распределения значений в выборках не являются "нормальными", применим непараметрический  тест Манна-Уитни для сравнения двух независимых выборок.')
    st.markdown('#### H0 : нулевая гипотиза: выборки не имеют значимых различий.')
    st.markdown('#### H1 : альтернативная гипотеза: выборки  имеют значимые различия.')
    st.markdown('Если p > 0.05: Нет досточных оснований, чтобы отклонить H0.')
    st.markdown('Если p < 0.05 Есть достаточно оснований, чтобы отклонить H0.')
    st.write('Уровень значимости p =', p)
    if p > 0.05:
        st.markdown(
            f'### Вывод: Мужчины не пропускают в течение года более {work_days} рабочих дней по болезни значимо чаще женщин.')
    elif p < 0.05:
        st.markdown(
            f'### Вывод: Мужчины пропускают в течение года более {work_days} рабочих дней по болезни значимо чаще женщин.')



elif app_mode == 'Разделение по возрасту':
    # выбор порога возраста
    min_age, max_age = min_max_age(df)
    st.markdown(':red[Выберите порог возраста]')
    age = st.selectbox('age', range(min_age, max_age))
    above, below, max_day, min_day = age_hipo(df, age, min_age)
    # выбор порога пропущенных дней
    st.markdown(':red[Выберите порог пропущенных дней]')
    work_days = st.slider('work_days', min_day, max_day)
    above = above.loc[above['Количество больничных дней'] >= work_days, 'Количество больничных дней']
    below = below.loc[below['Количество больничных дней'] >= work_days, 'Количество больничных дней']
    try:
        p = statistic(above, below)
    except:
        st.markdown('Выберете другой порог пропущенных дней ')
    st.markdown(
        f'_Требуется проверить гипотезу, что Работники старше {age} пропускают в течение года более {work_days} рабочих дней  по болезни значимо чаще своих более молодых коллег._')

    # распределения по выборкам
    fig = plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.title(f'Младше {age} лет')
    plt.hist(np.array(below), bins=4)
    plt.subplot(1, 2, 2)
    plt.title(f'Старше {age} лет')
    plt.hist(np.array(above), bins=4)
    fig.suptitle('Распределение пропущенных дней для работников по выборкам')
    st.pyplot(fig)
    st.markdown(
        'Распределения значений в выборках не является "нормальными", применим непараметрический  тест Манна-Уитни для сравнения двух независимых выборок.')
    st.markdown('#### H0 : нулевая гипотиза: выборки не имеют значимых различий.')
    st.markdown('#### H1 : альтернативная гипотеза: выборки  имеют значимые различия.')
    st.markdown('Если p > 0.05: Нет досточных оснований, чтобы отклонить H0.')
    st.markdown('Если p < 0.05 Есть достаточно оснований, чтобы отклонить H0.')
    st.write('Уровень значимости p =', p)
    if p > 0.05:
        st.markdown(
            f'### Вывод: Работники старше  {age} лет не пропускают в течение года более {work_days} рабочих дней по болезни значимо чаще своих более молодых коллег..')
    elif p < 0.05:
        st.markdown(
            f'### Вывод: Работники старше  {age} лет пропускают в течение года более {work_days} рабочих дней по болезни значимо чаще своих более молодых коллег..')


