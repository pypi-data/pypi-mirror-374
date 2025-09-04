# 전자결제(PG) 서비스 소개

헥토파이낸셜 전자결제(PG)서비스는 신용카드, 실시간 계좌이체, 가상계좌, 휴대폰 결제, 상품권 결제 등 다양한 온라인 결제수단을 지원하는 통합 결제 서비스입니다.

#### Quick Link

[신용카드](https://develop.sbsvc.online/16/onlineDocList.do#item-433)  [계좌이체](https://develop.sbsvc.online/16/onlineDocList.do#item-443)  [가상계좌](https://develop.sbsvc.online/16/onlineDocList.do#item-453)  [010가상계좌](https://develop.sbsvc.online/16/onlineDocList.do#item-824)  [휴대폰결제](https://develop.sbsvc.online/16/onlineDocList.do#item-463)  [상품권결제](https://develop.sbsvc.online/16/onlineDocList.do#item-473)  [포인트다모아](https://develop.sbsvc.online/16/onlineDocList.do#item-533)  [페이코 간편결제](https://develop.sbsvc.online/16/onlineDocList.do#item-1023)  [카카오페이 간편결제](https://develop.sbsvc.online/16/onlineDocList.do#item-1061)  [네이버페이 간편결제](https://develop.sbsvc.online/16/onlineDocList.do#item-1112)  [삼성페이 간편결제](https://develop.sbsvc.online/16/onlineDocList.do#item-1269)  [신용카드 비/구인증 API](https://develop.sbsvc.online/16/onlineDocList.do#item-1046)

# 표준 연동규격서

# 1\. 개요

## 1.1 목적

본 문서는 헥토파이낸셜에서 제공하는 전자결제(PG) 표준결제창 연동 개발에 필요한 기술적 이해를 돕고 상세 규격을 정의하기 위해 작성 되었습니다.

## 1.2 대상

본 문서는 헥토파이낸셜 전자결제(PG) 시스템을 통해 결제를 수행하기 위한 고객사 개발자를 대상으로 합니다.

## 1.3 문서 규격

다음은 본 문서에서 언급하는 연동상의 일반적인 사항에 대하여 설명합니다.

*   요청/응답 파라미터 중 필수 필드는 '●' 기호를 사용하며, 선택 필드는 '○' 기호를 사용합니다.
*   요청/응답 파라미터의 데이터 타입은 다음과 같습니다.
    *   N : 숫자 형식의 문자열
    *   A : 알파벳 형식의 문자열
    *   H : 한글 형식의 문자열
*   요청/응답 파라미터의 길이는 평문을 UTF-8 인코딩한 값(Byte)을 기준으로 합니다.

## 1.4 기타

*   [여기](https://develop.sbsvc.online/21/bbsList.do?tx=R&articleSeq=149)에서 오프라인 문서를 다운로드 받을 수 있습니다. (온라인 문서는 항상 최신화 되어 있습니다.)
*   본 문서를 완독할 필요는 없습니다. 결제 수단 및 서비스별로 항목이 나누어져 있으니, 필요한 부분만 참고하시면 됩니다.
*   자주묻는질문(FAQ) [이동](https://develop.sbsvc.online/3/bbsList.do)

# 2\. 표준결제창(UI) 연동

헥토파이낸셜에서 제공하는 전자결제(PG) 표준결제창 연동 방법에 대해 기술합니다.

## 2.1 요약 설명

*   결제 수단별 요청 URI를 확인합니다.(\[[2.3 API URI](#item-432)\] 참고)
*   결제 수단별 요청 전문을 확인하여, 요청파라미터를 세팅한 후 POST방식으로 요청합니다.
*   개인/민감정보 관련 파라미터는 암호화 해야합니다.(\[[5.중요 정보 보안](#item-424)\] 참고)
*   헥토파이낸셜 결제창을 띄우고, 결제를 진행합니다.
*   결제 완료 화면에서 \[닫기\] 버튼을 누르면, 요청파라미터 nextUrl에 지정된 URL로 결과(응답파라미터)가 리턴됩니다.
*   사용자가 결제 도중 강제로 결제창을 종료할 시(세틀 결제창 'X'버튼), cancUrl 파라미터에 지정된 URL로 결과(응답 파라미터)가 리턴됩니다

## 2.2 주의 사항

*   **2022년 6월 15일부터, IE 브라우저 지원이 종료되오니, Edge 브라우저 사용해 주시기 바랍니다.**
*   **오페라 브라우저 사용을 삼가 주십시오. 일부 기능이 작동하지 않을 수 있습니다.**
*   **운영환경에서 상점아이디(mchtId)로 테스트 진행시 발생하는 비용은 가맹점 부담입니다.**
*   **요청은 POST method만을 사용합니다.**
*   **요청 파라미터는 연동규격서에 명시된 것만 사용하십시오. 그렇지 않을 경우 오류가 발생할 수 있습니다.**
*   **요청 파라미터에 :, &, ?, ', ", new line, <, > 등의 특수문자 사용을 삼가 주십시오.**
*   **요청 파라미터에 href, alert, javascript, console.log 등의 html태그 또는 예약어 사용을 삼가 주십시오. 해당 단어들이 포함될 경우 사용자의 의도와 관계 없이 제거됩니다.**
*   **요청 파라미터에 이모지 사용을 삼가 주십시오. 이모지가 포함될 경우 사용자의 의도와 관계 없이 제거됩니다.**
*   **응답 파라미터는 예고 없이 변동될  수 있습니다.**
*   **결제창 연동시 Iframe 사용하는 경우, 일부 브라우저나 기기에서 정상적으로 작동하지 않는 경우가 있으니, Iframe 사용을 삼가 주십시오.**
*   **nextUrl, notiUrl 파라미터**
    *   nextUrl : 헥토파이낸셜 결제창 완료 화면에서 고객이 '닫기' 버튼을 클릭한 경우 호출되는 URL입니다. 응답파라미터가 POST방식으로 전달되며, 고객이 결제창을 강제로 종료하는 경우(브라우저 'X'버튼) 호출되지 않습니다. nextUrl은 반드시 화면 처리 용도로만 사용하시고, DB처리는 notiUrl에서 하시기 바랍니다.  
         
    *   notiUrl : 헥토파이낸셜 결제서버에서  결제가 성공적으로 처리된 경우, 가맹점측으로 Server To Server 커넥션을 맺어 응답 파라미터를 POST방식으로 전송합니다. 결제창 강제 종료 여부에 관계없이 승인성공시 응답파라미터가 전송됩니다.  
         
    *   따라서 nextUrl에서는 전달된 응답파라미터로 결제 결 과를 보여주는 화면 처리를 하시고, 가맹점측 결제 관련 DB처리는 반드시 notiUrl에서 처리해 주시기 바랍니다.
*   **notiUrl 해쉬 체크**
    *   **데이터 위변조를 체크하기 위해서 notiUrl로 수신받은 해쉬데이터를 반드시 가맹점DB와 검증하는** **절차를 진행해야 합니다. 일치하는 경우에만 고객에게 서비스를 제공해야 합니다.**
    *   해쉬데이터 체크 방법과 알고리즘은 노티 전문의 pktHash 파라미터를 참고해 주십시오.
*   **nextUrl, notiUrl, cancUrl 프로토콜**
    *   HTTP 사용시 브라우저 정책에 위반되어(cross-origin 등) 결제창이 정상적으로 동작하지 않을 수 있습니다.
    *   따라서 HTTPS 사용을 권장드립니다.

## 2.3 API URI

헥토파이낸셜 결제창(UI) 서버 도메인 이름은 다음과 같습니다.

 
| 구분  | 도메인 이름 |
| --- | --- |
| 테스트베드 | tbnpg.settlebank.co.kr |
| 상용 환경 | npg.settlebank.co.kr |

헥토파이낸셜 결제창(UI) API URI는 다음과 같습니다.

   
| 기능 구분 | 결제 수단 | URI | HTTP  <br>Method |
| --- | --- | --- | --- |
| 표준결제창 (UI) | 신용카드 | https://{domain}/card/main.do | POST |
| 신용카드-직호출 | https://{domain}/card/cardDirect.do |
| 신용카드-외화결제창 | https://{domain}/card/abroad/main.do |
| 계좌이체 | https://{domain}/bank/main.do |
| 가상계좌 | https://{domain}/vbank/main.do |
| 휴대폰결제 | https://{domain}/mobile/main.do |
| 틴캐시상품권 | https://{domain}/gift/teenCash/main.do |
| 해피머니상품권 | https://{domain}/gift/happyMoney/main.do |
| 컬쳐랜드상품권(컬쳐캐쉬) | https://{domain}/gift/cultureCash/main.do |
| 스마트문상 | https://{domain}/gift/smartCash/main.do |
| 도서상품권 | https://{domain}/gift/booknlife/main.do |
| 티머니 | https://{domain}/tmoney/main.do |
| 포인트다모아 | https://{domain}/point/main.do |
| 간편결제 | https://{domain}/corp/main.do |

## 2.4 요청 및 응답 헤더

 
| 구분  | 내용  |
| --- | --- |
| 요청  | Content-type=application/x-www-form-urlencoded; charset=UTF-8 |
| 응답  | Content-type=text/html; charset=UTF-8 |

## 2.5 요청 파라미터 검증

필수값 누락, HASH 데이터 불일치, 길이체크 등 파라미터 검증 후 이상이 있을 경우 아래와 같은 응답 코드를 반환합니다.

```
{
    "outRsltMsg" : "결제 요청 정보 누락 (상품명)",
    "mchtTrdNo" : "ORDER20211231100000",
    "outRsltCd" : "1008",
    "outStatCd" : "0031",
    "mchtId" : "nxca_jt_il"
}
```

## 2.6 연동 스크립트 예시

연동시 가맹점측 편의를 위해 연동 스크립트를 제공하고 있습니다.

 
| 구분  | URL |
| --- | --- |
| 테스트베드 | https://tbnpg.settlebank.co.kr/resources/js/v1/SettlePG\_v1.2.js |
| 상용 환경 | https://npg.settlebank.co.kr/resources/js/v1/SettlePG\_v1.2.js |

- - -

연동 스크립트 사용 예시는 다음과 같습니다.

```
SETTLE_PG.pay({
    env: "https://tbnpg.settlebank.co.kr",
    mchtId: "nxca_jt_il",
    method: "card",
    trdDt: "20211231",
    trdTm: "100000",
    mchtTrdNo: "ORDER20211231100000",
    mchtName: "헥토파이낸셜",
    mchtEName: "Hecto Financial",
    pmtPrdtNm: "테스트상품",
    trdAmt: "AntV/eDpxIaKF0hJiePDKA==",
    mchtCustNm: "홍길동",
    custAcntSumry: "헥토파이낸셜",
    notiUrl: "https://example.com/notiUrl",
    nextUrl: "https://example.com/nextUrl",
    cancUrl: "https://example.com/cancUrl",
    mchtParam: "name=HongGilDong&age=25",
    custIp: "127.0.0.1",
    pktHash: "f395b6725a9a18f2563ce34f8bc76698051d27c05e5ba815f463f00429061c0c",
    ui: {
        type: "popup",
        width: "430",
        height: "660"
    }
}, function(rsp){
    console.log(rsp);
});
```

아이프레임 닫기

```
parent.postMessage(JSON.stringify({action:"HECTO_IFRAME_CLOSE", params: _PAY_RESULT}), "*");
```

아이프레임 너비 조절

```
parent.postMessage(JSON.stringify({action:"HECTO_IFRAME_RESIZE", params: {width:"500px"}}), "*");
```

아이프레임 기본사이즈로

```
parent.postMessage(JSON.stringify({action:"HECTO_IFRAME_RETURNSIZE"}), "*");
```

## 2.7 스크립트 파라미터 정의

   
| 파라미터 | 타입  | 설명  | 필수 여부 |
| --- | --- | --- | --- |
| env | string | 결제 시스템의 환경을 설정합니다.  <br>테스트 환경: 'https://tbnpg.settlebank.co.kr'  <br>운영 환경: 'https://npg.settlebank.co.kr' | Y   |
| mchtId | string | 상점 ID입니다. 상점에 고유한 값이 부여됩니다. | Y   |
| method | string | 결제 방법을 설정합니다. 예: 'card' 등 | Y   |
| trdDt | string | 거래일자를 설정합니다. 형식: 'YYYYMMDD' | Y   |
| trdTm | string | 거래시간을 설정합니다. 형식: 'HHMMSS' | Y   |
| mchtTrdNo | string | 상점 거래번호입니다. 상점에서 고유하게 생성된 거래 번호 | Y   |
| mchtName | string | 상점명입니다. 예: '헥토파이낸셜' | Y   |
| mchtEnName | string | 상점 영문명입니다. 예: 'Hecto Financial' | Y   |
| pmtPrdtNm | string | 결제 상품명입니다. 예: '테스트상품' | Y   |
| trdAmt | string | 결제 금액을 암호화된 값으로 전달합니다. | Y   |
| mchtCustNm | string | 상점 고객명입니다. 예: '홍길동' | Y   |
| custAcntSumry | string | 고객 계좌 요약 정보입니다. | Y   |
| notiUrl | string | 결제 상태 변경 알림을 받을 URL입니다. | Y   |
| nextUrl | string | 결제 완료 후 리턴될 URL입니다. | Y   |
| cancUrl | string | 결제 취소 후 리턴될 URL입니다. | Y   |
| mchtParam | string | 상점 고유의 파라미터를 전달합니다. 예: 'name=HongGilDong&age=25' | Y   |
| custIp | string | 고객의 IP 주소입니다. 예: '127.0.0.1' | Y   |
| pktHash | string | 암호화된 결제 요청 데이터의 해시 값입니다. | Y   |
| ui  | object | 결제 UI 설정입니다. 결제창의 호출 방식 및 크기를 설정합니다. | Y   |

*   스크립트 ui 객체

   
| 파라미터 | 타입  | 설명  | 필수 여부 |
| --- | --- | --- | --- |
| type | string | 결제창 호출 방식. 선택할 수 있는 값:  <br>\- popup : 팝업 창 방식  <br>\- iframe : iframe 형식  <br>(지양하는 방식)  <br>\- self : 동일 창에서 호출  <br>\- blank :새 창에서 호출 | Y   |
| width | string | 결제창의 너비 (단위: px) | Y   |
| height | string | 결제창의 높이 (단위: px) | Y   |

## 2.8 샘플 소스 제공

*   헥토파이낸셜 결제창 연동을 용이하게 하기 위해서, 샘플 소스를 제공합니다.
*   헥토파이낸셜에서 제공하는 샘플 소스는 연동을 위한 기본적인 사항만 기재되어 있으므로, 실제 개발시에는 고객사의 환경에 맞게 연동하시기 바랍니다.

1.  **헥토파이낸셜 개발자 지원 사이트 접속** [클릭!](https://develop.sbsvc.online)
2.  **상단 메뉴 \[개발자 포럼\] > \[[SDK 다운로드](https://develop.sbsvc.online/21/bbsList.do)\]에서 샘플 소스 다운로드**
    *   표준결제창(UI) [클릭!](https://develop.sbsvc.online/21/bbsList.do?tx=R&articleSeq=209)
    *   신용카드 비/구인증 API(Non-UI) [클릭!](https://develop.sbsvc.online/21/bbsList.do?tx=R&articleSeq=210)
    *   가상계좌 API(Non-UI) [클릭!](https://develop.sbsvc.online/21/bbsList.do?tx=R&articleSeq=216)
3.  **config.xxx 설정 변경**
    *   샘플 소스 설정파일입니다. 상점아이디, 암호화 키, 로그 디렉터리 등을 설정할 수 있습니다.
    *   테스트 환경에서는 디폴트 값을 사용하시면 됩니다.
    *   운영 환경에서는 헥토파이낸셜에서 발급받은 상점아이디 및 암호화 키를 설정하셔야 합니다.
4.  **notiUrl, nextUrl, cancUrl 요청 파라미터 값 변경**
    *   notiUrl : 헥토파이낸셜에서 Server To Server로 전달되는 응답 파라미터를 수신하는 URL 기재
    *   nextUrl : 헥토파이낸셜 결제창 결제 완료 후 전환되는 가맹점측 화면 URL 기재
    *   cancUrl : 헥토파이낸셜 결제창에서 고객이 강제 종료시 전환되는 가맹점측 화면 URL 기재
5.  **기타 주의 사항**
    *   JAVA(JSP) : log4j 설정 파일 자사에 맞게 변경 필요
    *   PHP : curl 및 openssl 패키지 설치 필요(php.ini 파일 주석 해제 필요)
    *   PHP 5.4 버전 이하인 경우 일부 함수가 작동하지 않을 수 있습니다.
    *   ASP 클래식의 경우 추가로 배포된 DLL파일(암복호화 모듈) 설치 필요합니다.
    *   ASP 클래식 DLL 가이드 [클릭!](https://develop.sbsvc.online/21/bbsList.do?tx=R&articleSeq=172)

# 3\. API서버 연동 (Non-UI)

결제 수단별 취소, 신용카드 빌키 결제, 휴대폰 월자동 결제, 가상계좌 채번 등의 API 서비스 연동 방법에 대해 기술합니다.

## 3.1 요약 설명

*   이용 하고자 하는 서비스별 [API URI](#item-582)를 확인합니다.
*   이용 하고자 하는 서비스별 요청 전문을 확인 후, 해당되는 요청 파라미터를 세팅합니다.
*   Server to Server 로 HTTP Connection 하여 [JSON 데이터](#item-584)로 요청/응답합니다.
*   개인/민감정보 관련 파라미터는 암호화해야 합니다. (\[[5.중요 정보 보안](#item-424)\] 참고)

## 3.2 API URI

헥토파이낸셜 API 서버 도메인 이름은 다음과 같습니다.

 
| 구분  | 도메인 이름 |
| --- | --- |
| 테스트베드 | tbgw.settlebank.co.kr |
| 상용 환경 | gw.settlebank.co.kr |

API 서버 URI는 다음과 같습니다.

   
| 기능구분 | 서비스 | URI | HTTP  <br>Method |
| --- | --- | --- | --- |
| 결제 API  <br>(Non-UI) | 신용카드 결제 및 빌키 결제 | https://{domain}/spay/APICardActionPay.do | POST |
| 신용카드 빌키 발급 | https://{domain}/spay/APICardAuth.do |
| 휴대폰 월자동결제 | https://{domain}/spay/APIService.do |
| 페이코 간편결제 승인 | https://{domain}/spay/APITrdPayco.do |
| 취소 API  <br>(Non-UI) | 신용카드 취소 | https://{domain}/spay/APICancel.do | POST |
| 계좌이체 취소 |
| 휴대폰결제 취소 |
| 틴캐시 취소 |
| 해피머니 취소 |
| 컬쳐랜드상품권(컬쳐캐쉬) 취소 |
| 스마트문상 취소 |
| 도서상품권 취소 |
| 티머니 취소 |
| 포인트다모아 취소 |
| 간편결제 취소 |
| 가상계좌 서비스 API  <br>(Non-UI) | 가상계좌 채번 | https://{domain}/spay/APIVBank.do | POST |
| 가상계좌 채번취소 | https://{domain}/spay/APIVBank.do |
| 가상계좌 환불 | https://{domain}/spay/APIRefund.do |
| 휴대폰 환불 API | 휴대폰결제 환불 | https://{domain}/spay/APIRefund.do | POST |
| 기타 서비스 API  <br>(Non-UI) | 신용카드 빌키 삭제 | https://{domain}/spay/APICardActionDelkey.do | POST |
| 실시간 거래 조회 | https://{domain}/spay/APITrdcheck.do |

## 3.3 요청 및 응답 헤더

 
| 구분  | 내용  |
| --- | --- |
| 요청  | Content-type=application/json; charset=UTF-8 |
| 응답  | Content-type=application/json; charset=UTF-8 |

## 3.4 JSON 요청 데이터 예시

다음은 신용카드 취소 요청 전문 JSON 예시입니다.

```
{
	"params" : {
		"mchtId" : "nxca_jt_il",
		"ver" : "0A19",
		"method" : "CA",
		"bizType" : "C0",
		"encCd" : "23",
		"mchtTrdNo" : "ORDER20211231100000",
		"trdDt" : "20211231",
		"trdTm" : "100000",
		"mobileYn" : "N",
		"osType" : "W"
	},
	"data" : {
		"pktHash" : "a2d6d597d55d7c9b689baa2e08c1ddf0ce71f4248c5b9b59fe61bfbf949543e1",
		"crcCd" : "KRW",
		"orgTrdNo" : "STFP_PGCAnxca_jt_il0211129135810M1494620",
		"cnclAmt" : "AntV/eDpxIaKF0hJiePDKA==",
		"cnclOrd" : "001",
		"cnclRsn" : "상품이 마음에 들지 않아서"
	}
}
```

# 4\. 연동 서버

## 4.1 서버 IP 주소

다음은 헥토파이낸셜 서버의 IP주소입니다.

   
| 구분  |     | 도메인 이름 | IP주소 |
| --- | --- | --- | --- |
| 결제창(UI) | 테스트 베드 | tbnpg.settlebank.co.kr | 61.252.169.51  <br>HTTPS(TCP/443) |
| 상용 환경 | npg.settlebank.co.kr | 14.34.14.25(primary) |
| 61.252.169.58(secondary) |
| 취소 및 기타 API서비스 (Non-UI) | 테스트 베드 | tbgw.settlebank.co.kr  <br>HTTPS(TCP/443) | 61.252.169.42 |
| 상용 환경 | gw.settlebank.co.kr  <br>HTTPS(TCP/443) | 14.34.14.21(primary) |
| 61.252.169.53(secondary) |
| 정산대사 API | 테스트 베드 | tb-nspay.settlebank.co.kr  <br>HTTPS(TCP/443) | 61.252.169.32 |
| 상용 환경 | nspay.settlebank.co.kr  <br>HTTPS(TCP/443) | 61.252.169.29 (primary) |
| 14.34.14.37 (secondary) |

 

*   헥토파이낸셜 PG차세대 시스템은 IDC센터 이중화 구성되어 있습니다.(상용 환경)  
    따라서 예고 없이 GLB시스템 운영으로 주센터와 보조센터 전환이 이루어질 수 있으며, DNS Lookup에 의한 접속을 권장하고 있습니다.  
    따라서 안내드린 2개의 공인 IP주소(상용)를 방화벽에서 접속허용 요청드리며, hosts파일 구성은 권장하지 않습니다.
*   만약 귀사의 내부 정책으로 인하여 hosts파일에 Domain주소를 고정설정으로 구성하시는 경우 헥토파이낸셜 IDC센터 전환시에는 아래와 같이 "#(코멘트) 표시된 IP주소"로 반드시 모든 서버의 hosts파일을 수작업으로 변경처리를 해야만 정상적으로 결제서비스를 이용하실 수 있습니다.
*   모든 통신은 HTTPS(TCP/443) 프로토콜을 사용하며, TLS 1.2 이상을 사용하여 접속하는것을 강력하게 권장드립니다. TLS 1.1 이하버전은 보안권고사항에 따라 사전에 통지 없이 지원이 중단 될 수 있습니다 

##### #<</etc/hosts or c:\\windows\\system32\\drivers\\etc\\hosts파일내용>>

```
#cat /etc/hosts
#<<추가>>
14.34.14.25 npg.settlebank.co.kr
#61.252.169.58 npg.settlebank.co.kr

14.34.14.21 gw.settlebank.co.kr
#61.252.169.53 gw.settlebank.co.kr
```

## 4.2 노티 서버

거래 완료 후 거래 결과를 헥토파이낸셜에서 고객사시스템(방화벽 Inbound 허용필요)으로 Notification처리하는 서버에 대한 방화벽 허용하여야 합니다.  
결제창 호출시 notiUrl로 고객사 페이지를 호출합니다. TCP Port번호는 notiUrl에 지정한 포트번호로 방화벽 허용해 주시면 됩니다.

  
| 서비스 | 구분  | IP  |
| --- | --- | --- |
| 테스트 베드 | Notification발송 | 61.252.169.22 |
| 상용 환경 | Notification발송 | 14.34.14.23(Primary center) |
| 61.252.169.24(Secondary center) |

*   예) notiUrl=https://abc.com:8443/abc.do
    *   Source IP : 위 목록의 헥토파이낸셜 노티서버
    *   Destination : 고객사 서버IP(abc.com), TCP/8443
*   노티와 결제창 nextUrl 결과 전달 또는 노티와 NON-UI 승인 응답 사이에는 수신 순서가 보장되지 않습니다.
*   결제창 결제 후 승인 노티 발송은 필수, 취소 노티 발송은 옵션입니다. 취소 노티가 필요하신 경우 서비스 오픈 전 헥토파이낸셜 담당자에게 발송 설정 요청 바랍니다.
*   노티의 인코딩 방식은 별도 요청이 없는 경우 EUC-KR로 설정됩니다.  
    EUC-KR, UTF-8 중 원하시는 인코딩 방식이 있으신 경우, 헥토파이낸셜 담당자에게 요청해주시기 바랍니다.

# 5\. 중요 정보 보안

## 5.1 개인정보 및 중요정보 암복호화(암호화/복호화)

데이터 송수신 시 개인정보/중요정보 필드에 대해서는 다음과 같은 암복호화(암호화/복호화)를 수행해야 합니다.

   
| 구분  | 항목  | 적용  | 인코딩 |
| --- | --- | --- | --- |
| 개인정보 | 알고리즘 | AES-256/ECB/PKCS5Padding | Base64 Encoding |
| 대상 필드 | 거래금액, 고객명, 휴대폰번호, 이메일 등  <br>(암호화 대상 필드는 개별 API의 요청 필드 규격의 비고란에 명시됩니다.) |     |     |

## 5.2 개인정보 암호키

개인 정보 및 중요정보 암복호화시 키 정보는 운영 환경에 따라 다르며 다음과 같습니다.  
단순 연동 테스트용으로는 테이블 첫번째 항목을 사용하십시오. 이후 연동이 성공적으로 이루어지면 헥토파이낸셜에서 발급하는 고유 키를 사용하십시오.

 
| 구분  | 암복호화 키 |
| --- | --- |
| 테스트베드 키(테스트용 공용 키) | pgSettle30y739r82jtd709yOfZ2yK5K |
| 상용 환경 키(가맹점 고유 키) | 서비스 이행 시 별도 통보 |

## 5.3 위변조 방지 알고리즘

요청 데이터의 위변조 여부를 검증하기 위해 추가적으로 해쉬키 검증을 수행하며, 해쉬키 생성 알고리즘은 다음과 같습니다.

   
| 구분  | 항목  | 적용  | 인코딩 |
| --- | --- | --- | --- |
| 위변조 | 알고리즘 | SHA-256 | Hex Encoding |

## 5.4 해쉬생성 인증키

단순 연동 테스트용으로는 테이블 첫번째 항목을 사용하시고, 연동이 성공적으로 이루어지면 헥토파이낸셜에서 발급하는 고유 키를 사용하십시오.

 
| 구분  | 인증 키 |
| --- | --- |
| 테스트베드 키(테스트용 공용 키) | ST1009281328226982205 |
| 상용 환경 키(가맹점 고유 키) | 서비스 이행시 별도 통보 |
