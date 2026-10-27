# geoconvert

KATEC(네이버 TM128) 좌표를 WGS84 경위도로 바꾸는 Splunk 검색 명령어. Splunk 9.x / 10.x.

## 설치

[Releases](https://github.com/hyunhonoh/geoconvert/releases)에서 `geoconvert-<버전>.tar.gz`를 받아
**앱 관리 → 파일에서 앱 설치**로 올리고 재시작.

## 사용

```
... | geoconvert <x필드> <y필드>
```

`x_long`(경도), `y_lat`(위도) 필드가 추가된다. 좌표가 없거나 숫자가 아닌 이벤트는 그대로 지나간다.

```
index=bootcamp
| geoconvert X좌표 Y좌표
| rename x_long as longitude, y_lat as latitude
| lookup skorea latitude, longitude
| stats count by featureId
| geom skorea
```

> 2.0.0부터 표준 KATEC(경도 원점 128°, 축척 0.9999, WGS84 측지계 변환)을 쓴다.
> 1.0은 경도가 약 0.5° 서쪽으로 치우친 값을 냈다.

## 라이선스

Apache-2.0. Splunk SDK for Python 포함 — [NOTICE](NOTICE)
