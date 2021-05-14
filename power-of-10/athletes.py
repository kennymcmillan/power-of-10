import requests
from bs4 import BeautifulSoup


def find_athletes(firstname=None, surname=None, club=None):
    url = f'https://www.thepowerof10.info/athletes/athleteslookup.aspx?'
    if surname is not None:
        url += f'surname={surname}&'
    if firstname is not None:
        url += f'firstname={firstname}&'
    if club is not None:
        url += f'club={club}'

    if firstname is None and surname is None and club is None:
        raise ValueError('Please input a firstname, surname or club')
    
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')

    results = soup.find('div', {'id': 'cphBody_pnlResults'}).find_all('tr')
    
    if 'cphBody_lblResultsErrorMessage' in str(results[0]):
        raise RuntimeError('Too many athletes found. Please change the search criteria.')

    data = []
    for r in results[1:-1]:
        row = BeautifulSoup(str(r), 'html.parser').find_all('td')
        data.append({
            'firstname': row[0].text, 
            'surname': row[1].text,
            'track': row[2].text,
            'road': row[3].text,
            'xc': row[4].text,
            'sex': row[5].text,
            'club': row[6].text,
            'athlete_id': str(row[7]).split('"')[3].split('=')[1]})

    return data


def get_athlete(athlete_id):
    if athlete_id is None:
        raise ValueError('Please input a valid athlete id.')

    url = f'https://www.thepowerof10.info/athletes/profile.aspx?athleteid={athlete_id}'
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    
    if soup.find('div', {'id': 'pnlMainGeneral'}).text.replace('\n','') == 'Profile not found':
        raise ValueError('Profile not found. Please input a valid athlete id')

    athlete_dets = soup.find('div', {'id': 'cphBody_pnlAthleteDetails'}).find_all('table')[1].text.replace('\n', '').split(':')
    athlete_abo = soup.find('div', {'id': 'cphBody_pnlAbout'}).find_all('table')[1]
    athlete_pb = soup.find('div', {'id': 'cphBody_divBestPerformances'}).find_all('tr')
    athlete_perf = soup.find('div', {'id': 'cphBody_pnlPerformances'}).find_all('table')[1].find_all('tr')
    athlete_rank = soup.find('div', {'id': 'cphBody_pnlMain'}).find('td', {'width': 220, 'valign': 'top'}).find_all('table')
    coach_dets = soup.find('div', {'id': 'cphBody_pnlAthletesCoached'})

    coaching = []
    if coach_dets is not None:
        s = coach_dets.find('table', {'class': 'alternatingrowspanel'}).find_all('tr')
        for i in s:
            dets = i.find_all('td')
            if dets[0].text != 'Name':
                coaching.append({
                    'name': dets[0].text,
                    'club': dets[1].text,
                    'age group': dets[2].text,
                    'sex': dets[3].text,
                    'best event': dets[4].text,
                    'rank': dets[5].text,
                    'age group': dets[6].text,
                    'year': dets[7].text,
                    'performance': dets[8].text
                })


    rankings = []
    if len(athlete_rank) > 2:
        for i in athlete_rank[2].find_all('tr'):
            dets = i.find_all('td')
            if dets[0].text != 'Event':
                rankings.append({
                    'event': dets[0].text,
                    'age group': dets[2].text,
                    'year': dets[3].text,
                    'rank': dets[4].text
                })
    
    performances = []
    for i in athlete_perf:
        if len(i.find_all('td')) > 1 and 'EventPerfPosVenueMeetingDate' != i.text:
            dets = i.find_all('td')
            performances.append({
                'event': dets[0].text,
                'value': dets[1].text,
                'position': [dets[5].text, dets[6].text],
                'venue': dets[9].text,
                'meeting': dets[10].text,
                'date': dets[11].text
            })

    pb = []
    for i in athlete_pb:
        if i.find('b').text != 'Event':
            pb.append({
                'event': i.find('b').text,
                'value': i.find_all('td')[1].text
            })
        
    if 'Login to add some details about this athlete' in athlete_abo:
        athlete_abo = None

    athlete = {
        'club': athlete_dets[1].replace('Gender',''),
        'gender': athlete_dets[2].replace('Age Group',''),
        'age group': athlete_dets[3].replace('County', ''),
        'county': athlete_dets[4].replace('Region',''),
        'region': athlete_dets[5].replace('Nation',''),
        'nation': athlete_dets[6].replace('Lead Coach',''),
        'lead coach': athlete_dets[7],
        'about': athlete_abo.text,
        'pb': pb,
        'performances': performances,
        'rankings': rankings,
        'coaching': coaching
    }

    return athlete
