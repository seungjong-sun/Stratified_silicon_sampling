호출 방식

python {코드명} {년도} {모델} {모델명}

ex) python main.py 2020 gpt 3.5
ex) python main_3pov.py 2024 claude sonnet

모든 코드는 자동으로 5번 돌아감
모든 코드에 대해 gpt 4, gpt 3.5, llama 13b, llama 70b, claude haiku, claude sonnet, claude opus 에 대해 돌릴 것.

실험 종류

1) 메인 실험
    main.py로 돌릴 것

2) sub population
    main_sub.py로 돌릴 것
    결과물은 각 인구통계하위 그룹별로 각각 나옴

3) down sampling
    main_down.py 로 돌릴 것
    결과물은 샘플 사이즈 별로 나옴

4) Prompt 인칭 변경
    main_3pov.py 로 돌릴 것

5) Prompt 순서 변경
    anes2020.py or anes2024.py의 'query'에서, biden과 trump 순서를 변경하고 돌릴 것 (저장필수)
    main.py로 돌릴 것
    유일하게 코드 수정이 필요한 부분이니, 실험 마지막에 돌리고, 돌린 후 원상복귀 할 것.
    [중요] 원본은 트럼프 - 바이든 순서임!
    