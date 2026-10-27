# geoconvert

KATEC(네이버 TM128) 좌표를 WGS84 경위도로 바꾸는 Splunk 검색 명령어. Splunk 9.x / 10.x.

## 설치

[Releases](https://github.com/hyunhonoh/geoconvert/releases)에서 `geoconvert-<버전>.tar.gz`를 받아
**앱 관리 → 파일에서 앱 설치**로 올리고 재시작.

## 사용

```
... | geoconvert <x필드> <y필드>
```

`x_long`(경도), `y_lat`(위도)가 추가된다. 좌표가 없거나 숫자가 아니거나 KATEC 범위를 벗어나면 빈 값.

```
index=main sourcetype=stores
| geoconvert X좌표 Y좌표
| geostats latfield=y_lat longfield=x_long count
```

필드명은 실제 추출된 이름으로 쓴다(`| fieldsummary`로 확인). 앱의 **좌표 변환 예제** 대시보드에서 바로 확인할 수 있다.

## 1.0에서 올릴 때

1.0은 KATEC 정의가 틀려 경도가 약 0.5°(약 45km) 서쪽으로 나왔다. 2.0은 같은 입력에 대해 그만큼 동쪽 값을 낸다.
1.0 결과로 만든 lookup·summary index는 다시 계산할 것.

## 라이선스

Apache-2.0. Splunk SDK for Python 포함 — [NOTICE](NOTICE)
