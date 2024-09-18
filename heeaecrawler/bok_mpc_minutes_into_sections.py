import pandas as pd
import ast

def get_section_Economic_Situation(startyear, endyear):
    # 경제 상황과 관련된 키워드 목록
    keywords_Economic_Situation = ['(가) 2017∼18년 경제전망',
                                    '(가) 국내외 경제동향 및 평가',
                                    '(가) 2017년 하반기 경제전망',
                                    '(가) 2017년 경제전망(수정)',
                                    '(가) 2017년 경제전망',
                                    '｢국내외 경제동향｣과 관련하여',
                                    '｢국내외경제 동향｣과 관련하여',
                                    '「국내외 경제동향」과 관련하여',
                                    '국내외 경제동향과 관련하여']
    
    # 외환 및 국제금융 동향과 관련된 키워드 목록
    keywords_section_Foreign_Currency = ['｢외환·국제금융 동향｣과 관련하여',
                                         '(나) 외환·국제금융 및 금융시장 동향',
                                         '(나) 외환·국제금융 동향',
                                         '｢외환․국제금융 동향｣과 관련하여']
    
    # 지정된 연도 범위에 대한 데이터 필터링
    filtered_df = df[df['date'].str[:4].astype(int).between(startyear, endyear)]
    
    yearly_results = {}  # 연도별 결과를 저장할 딕셔너리
    
    # 필터링된 데이터프레임의 각 행을 처리
    for year in range(startyear, endyear + 1):
        yearly_df = filtered_df[filtered_df['date'].str[:4].astype(int) == year]
        total_sentence_count = 0  # 해당 연도의 전체 문장 수를 저장할 변수
        content_counts = []  # 각 콘텐츠에 대한 문장 수를 저장할 리스트
        
        for idx, row in yearly_df.iterrows():
            content_str = row['content']
            try:
                # 'content' 열의 문자열을 리스트로 변환
                content_list = ast.literal_eval(content_str)
                current_section = None  # 현재 섹션을 저장할 변수
                content_sentence_count = 0  # 현재 콘텐츠의 문장 수를 저장할 변수
                
                # 리스트의 각 문장을 처리
                for sent in content_list:
                    if any(keyword in sent for keyword in keywords_Economic_Situation):
                        # 경제 상황 관련 키워드를 찾으면 섹션 캡처 시작
                        current_section = [sent]
                    elif current_section is not None:
                        if any(keyword in sent for keyword in keywords_section_Foreign_Currency):
                            # 외환 관련 키워드를 찾으면 섹션 캡처 종료
                            if current_section:
                                # 각 문장 끝에 구두점 추가
                                final_section = [s.strip() + '.' if not s.strip().endswith(('.', '!', '?')) else s.strip() for s in current_section]
                                content_sentence_count += len(final_section)
                            current_section = None
                        else:
                            current_section.append(sent)
                
                # 루프가 끝난 후에도 current_section에 내용이 남아있으면 문장 수 추가
                if current_section:
                    final_section = [s.strip() + '.' if not s.strip().endswith(('.', '!', '?')) else s.strip() for s in current_section]
                    content_sentence_count += len(final_section)
                
                # 현재 콘텐츠의 문장 수를 저장
                content_counts.append(content_sentence_count)
                total_sentence_count += content_sentence_count
        
            except (ValueError, SyntaxError) as e:
                return f"컨텐츠를 리스트로 변환하는 과정에서 오류 발생: {e}"
        
        # 연도별 결과 저장
        if content_counts:
            yearly_results[year] = {
                '총 콘텐츠 수': len(yearly_df),
                '각 콘텐츠당 문장 수': content_counts,
                '총 문장 수': total_sentence_count
            }
        else:
            # 문장 수가 0인 경우, 콘텐츠 및 문장 정보 디버깅 없이 결과 저장
            yearly_results[year] = {
                '총 콘텐츠 수': len(yearly_df),
                '각 콘텐츠당 문장 수': [],
                '총 문장 수': 0
            }
    
    return yearly_results if yearly_results else '해당 기간의 관련 내용을 찾을 수 없습니다.'

def get_section_Foreign_Currency(startyear, endyear):
    # 외환 및 국제금융 동향과 관련된 키워드 목록
    keywords_section_Foreign_Currency = ['｢외환·국제금융 동향｣과 관련하여',
                                         '「외환·국제금융 동향」과 관련하여',
                                         '(나) 외환·국제금융 및 금융시장 동향',
                                         '(나) 외환·국제금융 동향',
                                         '｢외환․국제금융 동향｣과 관련하여']
    
    keywords_section_Financial_Markets = ['｢금융시장 동향｣과 관련하여',
                                          '(다) 금융시장 동향']


    # 지정된 연도 범위에 대한 데이터 필터링
    filtered_df = df[df['date'].str[:4].astype(int).between(startyear, endyear)]
    
    yearly_results = {}  # 연도별 결과를 저장할 딕셔너리
    
    # 필터링된 데이터프레임의 각 행을 처리
    for year in range(startyear, endyear + 1):
        yearly_df = filtered_df[filtered_df['date'].str[:4].astype(int) == year]
        total_sentence_count = 0  # 해당 연도의 전체 문장 수를 저장할 변수
        content_counts = []  # 각 콘텐츠에 대한 문장 수를 저장할 리스트
        
        for idx, row in yearly_df.iterrows():
            content_str = row['content']
            try:
                # 'content' 열의 문자열을 리스트로 변환
                content_list = ast.literal_eval(content_str)
                current_section = None  # 현재 섹션을 저장할 변수
                content_sentence_count = 0  # 현재 콘텐츠의 문장 수를 저장할 변수
                
                # 리스트의 각 문장을 처리
                for sent in content_list:
                    if any(keyword in sent for keyword in keywords_section_Foreign_Currency):
                        # 경제 상황 관련 키워드를 찾으면 섹션 캡처 시작
                        current_section = [sent]
                    elif current_section is not None:
                        if any(keyword in sent for keyword in keywords_section_Financial_Markets):
                            # 외환 관련 키워드를 찾으면 섹션 캡처 종료
                            if current_section:
                                # 각 문장 끝에 구두점 추가
                                final_section = [s.strip() + '.' if not s.strip().endswith(('.', '!', '?')) else s.strip() for s in current_section]
                                content_sentence_count += len(final_section)
                            current_section = None
                        else:
                            current_section.append(sent)
                
                # 루프가 끝난 후에도 current_section에 내용이 남아있으면 문장 수 추가
                if current_section:
                    final_section = [s.strip() + '.' if not s.strip().endswith(('.', '!', '?')) else s.strip() for s in current_section]
                    content_sentence_count += len(final_section)
                
                # 현재 콘텐츠의 문장 수를 저장
                content_counts.append(content_sentence_count)
                total_sentence_count += content_sentence_count
        
            except (ValueError, SyntaxError) as e:
                return f"컨텐츠를 리스트로 변환하는 과정에서 오류 발생: {e}"
        
        # 연도별 결과 저장
        if content_counts:
            yearly_results[year] = {
                '총 콘텐츠 수': len(yearly_df),
                '각 콘텐츠당 문장 수': content_counts,
                '총 문장 수': total_sentence_count
            }
        else:
            # 문장 수가 0인 경우, 콘텐츠 및 문장 정보 디버깅 없이 결과 저장
            yearly_results[year] = {
                '총 콘텐츠 수': len(yearly_df),
                '각 콘텐츠당 문장 수': [],
                '총 문장 수': 0
            }
    
    return yearly_results if yearly_results else '해당 기간의 관련 내용을 찾을 수 없습니다.'

def get_section_Financial_Markets(startyear, endyear):
    
    keywords_section_Financial_Markets = ['｢금융시장 동향｣과 관련하여',
                                          '「금융시장 동향」과 관련하여',
                                          '(다) 금융시장 동향',
                                          '｢금융시장 동향｣ 보고와 관련하여',
                                          '｢금융시장동향｣ 보고와 관련하여']

    keyword_section_Governments_View = ['(4) 정부측 열석자 발언',
                                        '(\x1f4\x1f) 정부측 열석자 발언']

    keywords_section_Monetary_Policy = ['이상과 같은 의견교환을 바탕으로 ｢통화정책방향｣에 관해 다음과 같은 토론이 있었음.',
                                        '이상과 같은 의견교환을 바탕으로 ｢통화정책 방향｣에 관해 다음과 같은 토론이 있었음.',
                                        '이상과 같은 의견교환을 바탕으로 실시된 위원들의  ｢통화정책 방향｣에 관한 토론은 다음과 같음',
                                        '(다) ｢통화정책방향｣에 관한 토론',
                                        '(라) ｢통화정책방향｣에 관한 토론']
    keywords_section_temporary = keyword_section_Governments_View + keywords_section_Monetary_Policy 

    # 지정된 연도 범위에 대한 데이터 필터링
    filtered_df = df[df['date'].str[:4].astype(int).between(startyear, endyear)]
    
    yearly_results = {}  # 연도별 결과를 저장할 딕셔너리
    
    # 필터링된 데이터프레임의 각 행을 처리
    for year in range(startyear, endyear + 1):
        yearly_df = filtered_df[filtered_df['date'].str[:4].astype(int) == year]
        total_sentence_count = 0  # 해당 연도의 전체 문장 수를 저장할 변수
        content_counts = []  # 각 콘텐츠에 대한 문장 수를 저장할 리스트
        
        for idx, row in yearly_df.iterrows():
            content_str = row['content']
            try:
                # 'content' 열의 문자열을 리스트로 변환
                content_list = ast.literal_eval(content_str)
                current_section = None  # 현재 섹션을 저장할 변수
                content_sentence_count = 0  # 현재 콘텐츠의 문장 수를 저장할 변수
                
                # 리스트의 각 문장을 처리
                for sent in content_list:
                    if any(keyword in sent for keyword in keywords_section_Financial_Markets):
                        # 경제 상황 관련 키워드를 찾으면 섹션 캡처 시작
                        current_section = [sent]
                    elif current_section is not None:
                        if any(keyword in sent for keyword in keywords_section_temporary):
                            # 외환 관련 키워드를 찾으면 섹션 캡처 종료
                            if current_section:
                                # 각 문장 끝에 구두점 추가
                                final_section = [s.strip() + '.' if not s.strip().endswith(('.', '!', '?')) else s.strip() for s in current_section]
                                content_sentence_count += len(final_section)
                            current_section = None
                        else:
                            current_section.append(sent)
                
                # 루프가 끝난 후에도 current_section에 내용이 남아있으면 문장 수 추가
                if current_section:
                    final_section = [s.strip() + '.' if not s.strip().endswith(('.', '!', '?')) else s.strip() for s in current_section]
                    content_sentence_count += len(final_section)
                
                # 현재 콘텐츠의 문장 수를 저장
                content_counts.append(content_sentence_count)
                total_sentence_count += content_sentence_count
        
            except (ValueError, SyntaxError) as e:
                return f"컨텐츠를 리스트로 변환하는 과정에서 오류 발생: {e}"
        
        # 연도별 결과 저장
        if content_counts:
            yearly_results[year] = {
                '총 콘텐츠 수': len(yearly_df),
                '각 콘텐츠당 문장 수': content_counts,
                '총 문장 수': total_sentence_count
            }
        else:
            # 문장 수가 0인 경우, 콘텐츠 및 문장 정보 디버깅 없이 결과 저장
            yearly_results[year] = {
                '총 콘텐츠 수': len(yearly_df),
                '각 콘텐츠당 문장 수': [],
                '총 문장 수': 0
            }
    
    return yearly_results if yearly_results else '해당 기간의 관련 내용을 찾을 수 없습니다.'

def get_section_Governments_View(startyear, endyear):
    keyword_section_Governments_View = ['(4) 정부측 열석자 발언',
                                        '(\x1f4\x1f) 정부측 열석자 발언',
                                        '정부측 열석자 발언']

    keywords_section_Monetary_Policy = ['이상과 같은 의견교환을 바탕으로 ｢통화정책방향｣에 관해 다음과 같은 토론이 있었음.',
                                        '이상과 같은 의견교환을 바탕으로 ｢통화정책 방향｣에 관해 다음과 같은 토론이 있었음.',
                                        '이상과 같은 의견교환을 바탕으로 실시된 위원들의  ｢통화정책 방향｣에 관한 토론은 다음과 같음',
                                        '(다) ｢통화정책방향｣에 관한 토론',
                                        '(라) ｢통화정책방향｣에 관한 토론']

    keywords_section_Participants_Views = ['(4) 한국은행 기준금리 결정에 관한 위원별 의견 개진',
                                           '(5) 한국은행 기준금리 결정에 관한 위원별 의견 개진',
                                           '(5) 한국은행 기준금리 결정에 관한 위원별 의견개진',
                                           '(\x1f5\x1f) 한국은행 기준금리 결정에 관한 위원별 의견개진',
                                           '(\x1f5\x1f) 한국은행 기준금리 결정에 관한 위원별 의견 개진']

    keywords_section_etc = ['(６) 심의결과', '\x15桤灧\x00\x00\x00\x00\x15물가부분과 관련하여']
    
    keywords_section_temporary_2 = keywords_section_Monetary_Policy + keywords_section_Participants_Views + keywords_section_etc

    # 지정된 연도 범위에 대한 데이터 필터링
    filtered_df = df[df['date'].str[:4].astype(int).between(startyear, endyear)]
    
    yearly_results = {}  # 연도별 결과를 저장할 딕셔너리
    
    # 필터링된 데이터프레임의 각 행을 처리
    for year in range(startyear, endyear + 1):
        yearly_df = filtered_df[filtered_df['date'].str[:4].astype(int) == year]
        total_sentence_count = 0  # 해당 연도의 전체 문장 수를 저장할 변수
        content_counts = []  # 각 콘텐츠에 대한 문장 수를 저장할 리스트
        
        for idx, row in yearly_df.iterrows():
            content_str = row['content']
            try:
                # 'content' 열의 문자열을 리스트로 변환
                content_list = ast.literal_eval(content_str)
                current_section = None  # 현재 섹션을 저장할 변수
                content_sentence_count = 0  # 현재 콘텐츠의 문장 수를 저장할 변수
                
                # 리스트의 각 문장을 처리
                for sent in content_list:
                    if any(keyword in sent for keyword in keyword_section_Governments_View):
                        # 섹션을 시작할 때 current_section을 초기화
                        current_section = [sent]
                    elif current_section is not None:
                        if any(keyword in sent for keyword in keywords_section_temporary_2) or len(current_section) > 50:  # 섹션이 너무 길어지면 종료
                            # 섹션 종료 처리
                            if current_section:
                                final_section = [s.strip() + '.' if not s.strip().endswith(('.', '!', '?')) else s.strip() for s in current_section]
                                content_sentence_count += len(final_section)
                            current_section = None  # 종료 후 current_section을 초기화
                        else:
                            # 섹션이 끝나지 않았을 때만 문장 추가
                            current_section.append(sent)
                            
                # 루프가 끝난 후에도 current_section에 남아있으면 문장 수 추가
                if current_section:
                    final_section = [s.strip() + '.' if not s.strip().endswith(('.', '!', '?')) else s.strip() for s in current_section]
                    content_sentence_count += len(final_section)
                
                # 현재 콘텐츠의 문장 수를 저장
                content_counts.append(content_sentence_count)
                total_sentence_count += content_sentence_count
        
            except (ValueError, SyntaxError) as e:
                return f"컨텐츠를 리스트로 변환하는 과정에서 오류 발생: {e}"
        
        # 연도별 결과 저장
        if content_counts:
            yearly_results[year] = {
                '총 콘텐츠 수': len(yearly_df),
                '각 콘텐츠당 문장 수': content_counts,
                '총 문장 수': total_sentence_count
            }
        else:
            # 문장 수가 0인 경우, 콘텐츠 및 문장 정보 디버깅 없이 결과 저장
            yearly_results[year] = {
                '총 콘텐츠 수': len(yearly_df),
                '각 콘텐츠당 문장 수': [],
                '총 문장 수': 0
            }
    
    return yearly_results if yearly_results else '해당 기간의 관련 내용을 찾을 수 없습니다.'

def get_section_Monetary_Policy(startyear, endyear):
    keywords_section_Monetary_Policy = [
        '이상과 같은 의견교환을 바탕으로 ｢통화정책방향｣에 관해 다음과 같은 토론이 있었음.',
        '이상과 같은 의견교환을 바탕으로 ｢통화정책 방향｣에 관해 다음과 같은 토론이 있었음.',
        '이상과 같은 의견교환을 바탕으로 실시된 위원들의  ｢통화정책 방향｣에 관한 토론은 다음과 같음',
        '이상과 같은 의견교환을 바탕으로 ｢통화정책방향｣에 관해 다음과 같은 토론이 있었음',
        '(다) ｢통화정책방향｣에 관한 토론',
        '(라) ｢통화정책방향｣에 관한 토론'
    ]

    keywords_section_Participants_Views = [
        '(4) 한국은행 기준금리 결정에 관한 위원별 의견 개진',
        '(5) 한국은행 기준금리 결정에 관한 위원별 의견 개진',
        '(5) 한국은행 기준금리 결정에 관한 위원별 의견개진',
        '(\x1f5\x1f) 한국은행 기준금리 결정에 관한 위원별 의견개진',
        '(\x1f5\x1f) 한국은행 기준금리 결정에 관한 위원별 의견 개진',
        '(\x1f4\x1f) 한국은행 기준금리 결정에 관한 위원별 의견 개진',
        '이상과 같은 토론에 이어 한국은행 기준금리 결정에 관한 위원별 의견개진이 있었음'
    ]

    keywords_section_etc_2 = [
        '이상과 같은 토론에 이어 콜금리 목표 조정여부 및 조정폭에 관한 위원별 의견 개진이 있었음',
        '이상과 같은 토론에 이어 콜금리 목표 조정여부 및 조정폭에 관한 위원별 의견개진이 있었음'
    ]

    keywords_section_temporary_3 = keywords_section_Participants_Views + keywords_section_etc_2

    # 지정된 연도 범위에 대한 데이터 필터링
    filtered_df = df[df['date'].str[:4].astype(int).between(startyear, endyear)]

    yearly_results = {}  # 연도별 결과를 저장할 딕셔너리

    # 필터링된 데이터프레임의 각 행을 처리
    for year in range(startyear, endyear + 1):
        yearly_df = filtered_df[filtered_df['date'].str[:4].astype(int) == year]
        total_sentence_count = 0  # 해당 연도의 전체 문장 수를 저장할 변수
        content_counts = []  # 각 콘텐츠에 대한 문장 수를 저장할 리스트
        
        for idx, row in yearly_df.iterrows():
            content_str = row['content']
            try:
                # 'content' 열의 문자열을 리스트로 변환
                content_list = ast.literal_eval(content_str)
                current_section = []  # 현재 섹션을 저장할 리스트
                content_sentence_count = 0  # 현재 콘텐츠의 문장 수를 저장할 변수
                
                # 리스트의 각 문장을 처리
                for sent in content_list:
                    if any(keyword in sent for keyword in keywords_section_Monetary_Policy):
                        # 섹션 시작
                        if current_section:
                            # 섹션 종료 처리
                            final_section = [s.strip() + '.' if not s.strip().endswith(('.', '!', '?')) else s.strip() for s in current_section]
                            content_sentence_count += len(final_section)
                        current_section = [sent]
                    elif current_section:
                        if any(keyword in sent for keyword in keywords_section_temporary_3) or len(current_section) > 50:
                            # 섹션 종료 처리
                            final_section = [s.strip() + '.' if not s.strip().endswith(('.', '!', '?')) else s.strip() for s in current_section]
                            content_sentence_count += len(final_section)
                            current_section = []
                        else:
                            # 섹션 계속
                            current_section.append(sent)
                
                # 루프가 끝난 후에도 current_section에 남아있으면 문장 수 추가
                if current_section:
                    final_section = [s.strip() + '.' if not s.strip().endswith(('.', '!', '?')) else s.strip() for s in current_section]
                    content_sentence_count += len(final_section)
                
                # 현재 콘텐츠의 문장 수를 저장
                content_counts.append(content_sentence_count)
                total_sentence_count += content_sentence_count
        
            except (ValueError, SyntaxError) as e:
                return f"컨텐츠를 리스트로 변환하는 과정에서 오류 발생: {e}"
        
        # 연도별 결과 저장
        yearly_results[year] = {
            '총 콘텐츠 수': len(yearly_df),
            '각 콘텐츠당 문장 수': content_counts,
            '총 문장 수': total_sentence_count
        }
    
    return yearly_results if yearly_results else '해당 기간의 관련 내용을 찾을 수 없습니다.'

def get_section_Participants_Views(startyear, endyear):
    keywords_section_Participants_Views = [
        '(4) 한국은행 기준금리 결정에 관한 위원별 의견 개진',
        '(5) 한국은행 기준금리 결정에 관한 위원별 의견 개진',
        '(5) 한국은행 기준금리 결정에 관한 위원별 의견개진',
        '(\x1f5\x1f) 한국은행 기준금리 결정에 관한 위원별 의견개진',
        '(\x1f5\x1f) 한국은행 기준금리 결정에 관한 위원별 의견 개진',
        '(\x1f4\x1f) 한국은행 기준금리 결정에 관한 위원별 의견 개진',
        '이상과 같은 토론에 이어 콜금리 목표 조정여부에 관한 위원별 의견개진이 있었음',
        '이상과 같은 토론에 이어 한국은행 기준금리 결정에 관한 위원별 의견개진이 있었음',
        '이상과 같은 토론에 이어 한국은행 기준금리 설정에 관한 위원별 의견개진이 있었음',
        '이상과 같은 토론에 이어 콜금리 목표 조정여부 및 조정폭에 관한 위원별 의견개진이 있었음',
        '이상과 같은 토론에 이어 콜금리 목표 조정여부 및 조정폭에 관한 위원별 의견 개진이 있었음',
        '위원별로 한국은행 기준금리 조정에 대한 의견을 개진하였음'
    ]

    keywords_section_end = ['토의결론','심의결과'] #비어있을 수도 있음

    # 지정된 연도 범위에 대한 데이터 필터링
    filtered_df = df[df['date'].str[:4].astype(int).between(startyear, endyear)]

    yearly_results = {}  # 연도별 결과를 저장할 딕셔너리

    # 필터링된 데이터프레임의 각 행을 처리
    for year in range(startyear, endyear + 1):
        yearly_df = filtered_df[filtered_df['date'].str[:4].astype(int) == year]
        total_sentence_count = 0  # 해당 연도의 전체 문장 수를 저장할 변수
        content_counts = []  # 각 콘텐츠에 대한 문장 수를 저장할 리스트
        
        for idx, row in yearly_df.iterrows():
            content_str = row['content']
            try:
                # 'content' 열의 문자열을 리스트로 변환
                content_list = ast.literal_eval(content_str)
                current_section = []  # 현재 섹션을 저장할 리스트
                content_sentence_count = 0  # 현재 콘텐츠의 문장 수를 저장할 변수
                section_active = False  # 현재 섹션이 활성 상태인지 여부
                
                # 리스트의 각 문장을 처리
                for sent in content_list:
                    if any(keyword in sent for keyword in keywords_section_Participants_Views):
                        # 섹션 시작
                        if section_active:
                            # 섹션 종료 처리
                            final_section = [s.strip() + '.' if not s.strip().endswith(('.', '!', '?')) else s.strip() for s in current_section]
                            content_sentence_count += len(final_section)
                        current_section = [sent]
                        section_active = True
                    elif section_active:
                        if keywords_section_end and any(keyword in sent for keyword in keywords_section_end):
                            # 섹션 종료 처리
                            final_section = [s.strip() + '.' if not s.strip().endswith(('.', '!', '?')) else s.strip() for s in current_section]
                            content_sentence_count += len(final_section)
                            current_section = []
                            section_active = False
                        else:
                            # 섹션 계속
                            current_section.append(sent)
                
                # 루프가 끝난 후에도 current_section에 남아있으면 문장 수 추가
                if section_active:
                    final_section = [s.strip() + '.' if not s.strip().endswith(('.', '!', '?')) else s.strip() for s in current_section]
                    content_sentence_count += len(final_section)
                
                # 현재 콘텐츠의 문장 수를 저장
                content_counts.append(content_sentence_count)
                total_sentence_count += content_sentence_count
        
            except (ValueError, SyntaxError) as e:
                return f"컨텐츠를 리스트로 변환하는 과정에서 오류 발생: {e}"
        
        # 연도별 결과 저장
        yearly_results[year] = {
            '총 콘텐츠 수': len(yearly_df),
            '각 콘텐츠당 문장 수': content_counts,
            '총 문장 수': total_sentence_count
        }
    
    return yearly_results if yearly_results else '해당 기간의 관련 내용을 찾을 수 없습니다.'

# 함수 이름에서 섹션명을 추출하는 함수
def extract_section_name(func_name):
    return func_name.replace('get_section_', '').replace('Views', 'View')

# DataFrame을 만드는 함수
def create_df_for_sections(startyear, endyear):
    # 함수 목록
    section_funcs = {
        'Economic_Situation': get_section_Economic_Situation,
        'Foreign_Currency': get_section_Foreign_Currency,
        'Financial_Markets': get_section_Financial_Markets,
        'Governments_View': get_section_Governments_View,
        'Monetary_Policy': get_section_Monetary_Policy,
        'Participants_View': get_section_Participants_Views
    }
    
    # 빈 리스트로 DataFrame을 만들 준비
    df_rows = []

    # 'date'에서 연도를 추출하여 'year' 열 생성
    df['year'] = pd.to_datetime(df['date']).dt.year

    # 연도 필터링
    filtered_df = df[(df['year'] >= startyear) & (df['year'] <= endyear)]

    # 각 섹션 함수에 대해 처리
    for section_name, section_func in section_funcs.items():
        # 함수 결과를 가져옴
        section_result = section_func(startyear, endyear)
        
        # 결과를 연도별로 처리
        for year, data in section_result.items():
            for idx, sent_no in enumerate(data['각 콘텐츠당 문장 수']):
                df_rows.append({
                    'year': year,  # 연도
                    'date': filtered_df.iloc[idx]['date'],  # 해당 행의 날짜
                    'section': section_name,  # 섹션 이름
                    'sent-no': sent_no  # 문장 수
                })

    # DataFrame 생성
    final_df = pd.DataFrame(df_rows, columns=['year', 'date', 'section', 'sent-no'])
    
    return final_df

if __name__ == '__main__':
    df = pd.read_csv('C:/Users/kwkwo/sesac_studygroup/bok_mpc_minutes_data(edited).csv')
    final_df = create_df_for_sections(2005, 2017)

    final_df.to_csv('C:/Users/kwkwo/sesac_studygroup/bok_mpc_minutes_into_sections_data.csv', index=False)