# 6\. 신용카드 결제 (UI)

## 6.1 주의 사항

*   상점아이디 속성에 따라 화면이 분기됩니다.
    *   상점아이디가 일반 인증 결제로 설정되어 있는 경우 카드사 인증창이 나타납니다.
    *   상점아이디가 비인증 또는 구인증으로 설정되어 있는 경우 카드정보 입력창이 나타납니다.
*   신용카드 빌키(billKey)를 내려받고자 하는 경우, 빌키서비스를 별도 신청하셔야 합니다
*   빌키를 발급받은 경우, 해당 빌키로 2회차 결제 API 요청하시면 됩니다.(\[[신용카드 빌키 결제 API](#item-1047)\] 참고)
*   ※ 매출전표의 발행금액은 가맹점에서 전송하는 파라미터를 기준으로 표기되니 주의하시기 바랍니다.
    *   ex) 과세 가맹점에서 거래금액 1,000원을 다음과 같이 전송하는 경우
    *   1) 거래금액만 전송 : 과세 909, 부가세 91 로 표기
    *   2) 과세금액 900, 부가세금액 100 전송 : 과세 900, 부가세 100 으로 표기

## 6.2 요청 전문 (가맹점 → 헥토파이낸셜)

     
| 파라미터 | 이름  | 설명  | 타입(길이) | 필수  | 비고  |
| --- | --- | --- | --- | --- | --- |
| mchtId | 상점아이디 | 헥토파이낸셜에서 부여하는 고유 상점아이디  <br>nxca\_jt\_il:인증  <br>nxca\_jt\_bi:비인증  <br>nxca\_jt\_gu:구인증  <br>nxca\_ab\_bi:영문외화 비인증  <br>nxca\_ab\_il:영문외화 인증 | AN(10) | ●   | "nxca\_jt\_il" |
| method | 결제수단 | PG 서비스에 해당하는 결제 구분 코드 | AN(20) | ●   | "card"  <br>※ 고정값 |
| trdDt | 요청일자 | yyyyMMdd | N(8) | ●   | "20211231" |
| trdTm | 요청시간 | HH24MISS | N(6) | ●   | "100000" |
| mchtTrdNo | 상점주문번호 | 상점에서 생성하는 고유 주문번호  <br>※ 한글 제외 | AN(100) | ●   | "ORDER20211231100000" |
| mchtName | 상점한글명 | 상점한글명 | AHN(100) | ●   | "헥토파이낸셜" |
| mchtEName | 상점영문명 | 상점영문명 | AN(100) | ●   | "Hecto Financial" |
| pmtPrdtNm | 상품명 | 결제상품명 | AHN(128) | ●   | "테스트상품" |
| trdAmt | 거래금액 | 거래금액  <br>※ USD(달러) 사용시 100을 곱하여 전달  <br>※ AES 암호화 | N(12) | ●   | "1000" ※ KRW  <br>"100"   ※ USD  <br>ex) $ 1.00 → 100 (USD) |
| mchtCustNm | 고객명 | 고객명  <br>※ AES 암호화 | AHN(30) | ○   | "홍길동" |
| notiUrl | 결과처리 URL | 결제 후 결과 전달되는 페이지의 URL(Server To Server 연동 URL) | AN(250) | ●   | "https://example.com/notiUrl" |
| nextUrl | 결과화면 URL | 결제 후 결과 전달 및 이동페이지 URL | AN(250) | ●   | "https://example.com/nextUrl" |
| cancUrl | 결제취소 URL | 고객 강제 종료시 결과 전달 및 이동페이지 URL | AN(250) | ●   | "https://example.com/cancUrl" |
| mchtParam | 상점예약필드 | 기타 주문 정보를 입력하는 상점 예약 필드 | AHN(4000) | ○   | "name=HongGilDong&age=25" |
| email | 이메일 | 이메일 주소  <br>※ AES 암호화 | AN(60) | ○   | "HongGilDong@example.com" |
| prdtTerm | 상품제공기간 | yyyyMMddHHmmss  <br>값이 없으면 일반결제로 표기 | N(14) | ○   | "20221231235959" |
| mchtCustId | 상점고객아이디 | 상점에서 보내주는 고유 고객아이디 혹은 유니크키  <br>※ AES 암호화 | AN(50) | ○   | "HongGilDong" |
| taxTypeCd | 면세여부 | N:과세, Y:면세, G:복합과세  <br>공백일 경우 상점 설정에 따름 | A(1) | ○   | "N" |
| taxAmt | 과세금액 | 과세금액(복합과세일 경우 필수)  <br>※ AES 암호화 | N(12) | ○   | "909" |
| vatAmt | 부가세금액 | 부가세금액(복합과세일 경우 필수)  <br>※ AES 암호화 | N(12) | ○   | "91" |
| taxFreeAmt | 비과세금액 | 면세금액(복합과세일 경우 필수)  <br>※ AES 암호화 | N(12) | ○   | "0" |
| svcAmt | 봉사료 | 신용카드 봉사료  <br>※AES 암호화 | N(12) | ○   | "10" |
| instmtMon | 할부개월수 | 신용카드(일반) : 요청된 할부 개월 수가 할부 개월 리스트에 있을 경우 선택된 상태로 고정, 요청된 할부 개월 수가 할부 개월 리스트에 없을 경우 선택 할 수 있도록 할부 개월 수 리스트 노출  <br>신용카드-직호출 : 요청된 할부 개월 수로 결제 | N(2) | ○   | "00","2","3","4"... |
| cardType | 카드결제타입 | 3:앱카드 전용가능 카드사\[신한/삼성/현대/KB/농협/롯데\]  <br>6:현대카드 PayShot(카드사와 직접 제휴계약 진행 후 사용가능) | N(1) | ○   | "3" |
| chainUserId | 현대카드 PayShot ID | 카드사와 직접 제휴계약 진행 후 사용 가능 | AN(100) | ○   | ""  |
| cardGb | 특정카드사 코드 | 하나의 특정 카드사만 노출  <br>\[[신용카드 식별자](#item-545)\] 참고 | AN(4) | ○   | "NHC" |
| appScheme | 앱스키마 | (AppScheme://~)형식으로 사용되며, 자체앱을 구축하는 경우 사용  <br>\[[신용카드 WebView](#item-690)\] 참고 | AN(100) | ○   | "PAYAPPNAME://" |
| custIp | 고객 IP주소 | 상점 서버의 IP가 아닌, 고객 기기의 IP주소 | AN(15) | ○   | "127.0.0.1" |
| pktHash | hash데이터 | SHA256 방식으로 생성한 해쉬값  <br>\[[요청 전문 해쉬 코드](#item-772)\] 참고 | AN(200) | ●   | "f395b6725a9a18f2563ce34f8bc76698051d27c05e5ba815f463f00429061c0c" |

## 6.3 요청 전문 해쉬 코드

 
| 항목  | 조합 필드 |
| --- | --- |
| pktHash | 상점아이디 + 결제수단 + 상점주문번호 + 요청일자 + 요청시간 + 거래금액(평문) + 해쉬키 |

## 6.4 응답 전문 (헥토파이낸셜 → 가맹점)

신용카드 결제창에서 가맹점측으로 응답하는 컬럼을 다음과 같이 정의 합니다.

     
| 파라미터 | 이름  | 설명  | 타입(길이) | 필수  | 비고  |
| --- | --- | --- | --- | --- | --- |
| mchtId | 상점아이디 | 헥토파이낸셜에서 부여하는 고유 상점아이디  <br>nxca\_jt\_il:인증  <br>nxca\_jt\_bi:비인증  <br>nxca\_ks\_gu:구인증 | AN(10) | ●   | "nxca\_jt\_il" |
| outStatCd | 거래상태 | 거래상태코드(성공/실패)  <br>0021:성공  <br>0031:실패 | AN(4) | ●   | "0021" |
| outRsltCd | 거절코드 | 거래상태가 "0031"일 경우, 상세 코드 전달  <br>\[[거절 코드 표](#item-544)\] 참고 | AN(4) | ●   | "0000" |
| outRsltMsg | 결과메세지 | 결과 메세지 전달  <br>URL Encoding, UTF-8 | AHN(200) | ●   | "결제 요청 정보 누락 (상품명)" |
| method | 결제수단 | PG 서비스에 해당하는 결제 구분 코드 | AN(20) | ●   | "card"  <br>※ 고정값 |
| mchtTrdNo | 상점주문번호 | 상점에서 생성하는 고유 주문번호  <br>※ 한글 제외 | AN(100) | ●   | "ORDER20211231100000" |
| mchtCustId | 상점고객아이디 | 보내주는 고유 고객아이디 혹은 유니크 키  <br>※ AES 암호화 | AN(50) | ○   | "HongGilDong" |
| trdNo | 거래번호 | 헥토파이낸셜 거래번호 | AN(40) | ●   | "STFP\_PGCAnxca\_jt\_il0211129135810M1494620" |
| trdAmt | 거래금액 | 거래금액  <br>※ AES 암호화 | N(12) | ●   | "1000" |
| mchtParam | 상점예약필드 | 요청으로 받은 필드값을 응답으로 Bypass | AHN(4000) | ○   | "name=HongGilDong&age=25" |
| authDt | 승인일시 | 결제 승인 일시 | N(14) | ○   | "20211231100000" |
| authNo | 승인번호 | 신용카드 승인 번호 | N(15) | ○   | "30001234" |
| intMon | 할부개월 수 | 신용카드 할부 개월 수 | N(2) | ○   | "00" |
| fnNm | 카드사명 | 신용카드 카드사명 | AH(20) | ○   | "우리카드" |
| fnCd | 카드사코드 | 신용카드 카드사 코드 | AN(4) | ○   | "LTC" |
| pointTrdNo | 포인트 거래번호 | 고객이 포인트 결제를 했을 경우 포인트 결제 건 거래번호 | AN(40) | ○   | "STFP\_PGCAnxca\_jt\_il0211129135810M1494620" |
| pointTrdAmt | 포인트 거래금액 | 고객이 포인트 결제를 했을 경우 포인트 결제 금액  <br>※ AES 암호화 | N(12) | ○   | "1000" |
| cardTrdAmt | 신용카드 결제금액 | 고객이 할인 받은 금액 또는 포인트금액을 제외한 신용카드 결제금액  <br>※ AES 암호화 | N(12) | ○   | "4000" |
| billKey | 빌키(대문자 'K') | 빌키 서비스 이용시 발급되는 자동결제키. 2회차 결제 시 사용.  <br> ※ 빌키서비스 별도 신청 필요 | AN(50) | ●   | "SBILL\_0123456789" |

## 6.5 노티 전문 (헥토파이낸셜 → 가맹점)

거래가 정상적으로 완료되면, 헥토파이낸셜에서 가맹점으로 노티(결과통보) 메세지가 전송됩니다.

     
| 파라미터 | 이름  | 설명  | 타입(길이) | 필수  | 비고  |
| --- | --- | --- | --- | --- | --- |
| outStatCd | 거래상태 | 성공\[0021\] | N(4) | ●   | "0021" |
| trdNo | 거래번호 | 헥토파이낸셜에서 부여하는 고유 거래번호 | AN(40) | ●   | "STFP\_PGCAnxca\_jt\_il0211129135810M1494620" |
| method | 결제수단 | 신용카드\[CA\] | A(2) | ●   | "CA" |
| bizType | 업무구분 | 승인\[B0\], 취소\[C0\] | AN(2) | ●   | "B0" |
| mchtId | 상점아이디 | 헥토파이낸셜에서 부여하는 상점아이디 | AN(12) | ●   | "nxca\_jt\_il" |
| mchtTrdNo | 상점주문번호 | 상점에서 생성하는 고유 주문 번호 | AN(100) | ●   | "ORDER20211231100000" |
| mchtCustNm | 고객명 | 실제 결제자의 주문자명 | AHN(30) | ○   | "홍길동" |
| mchtName | 상점한글명 | 실 판매자명, 거래 요청시 실 판매자명이 없는 경우 헥토파이낸셜와 계약된 상점명 | AHN(20) | ○   | "헥토파이낸셜" |
| pmtprdNm | 상품명 | 고객이 주문한 결제 상품명 | AHN(128) | ○   | "테스트상품" |
| trdDtm | 거래일시 | 승인일시, 취소/부분취소거래 : 취소일시가 전달됩니다.  <br>형식:YYYYMMDDhhmmss | N(14) | ●   | "20211231100000" |
| trdAmt | 거래금액 | 거래금액 | N(12) | ○   | "1000" |
| svcAmt | 봉사료 | 신용카드 봉사료  <br>※ 오프라인거래이면서 봉사료 포함거래일 경우 전달. | N(12) | ○   | "0" |
| billKey | 자동결제키 | 자동결제 2회차를 위한 billKey발급 | AN(40) | ○   | "SBILL\_0123456789" |
| billKeyExpireDt | 자동결제키 유효기간 | YYMM | N(4) | ○   | "2212" |
| cardCd | 카드사코드 | 카드사 코드  <br>\[[신용카드 식별자 참고](#item-545)\] | AN(10) | ○   | "NHC" |
| cardNm | 카드명 | 카드사 명  <br>\[[신용카드 식별자 참고](#item-545)\] | AHN(20) | ○   | "NH 체크" |
| email | 고객이메일 | 상점 고객 이메일 | AN(60) | ○   | "HongGilDong@example.com" |
| mchtCustId | 상점고객아이디 | 상점 고객 아이디 | AN(50) | ○   | "HongGilDong" |
| cardNo | 카드번호 | 마스킹된 카드번호 123456\*\*\*\*\*\*7890  <br>\*상점 설정 정보에 따른 옵션값 | AN(20) | ○   | "123456\*\*\*\*\*\*7890" |
| cardApprNo | 카드승인번호 | 카드 승인 번호 | AN(15) | ○   | "30001234" |
| instmtMon | 할부개월수 | 할부 개월 수 | N(2) | ○   | "00" |
| instmtType | 할부타입 | 할부 개월이 카드사 이벤트에 속하는 경우 Y  <br>\*상점 설정 정보에 따른 옵션값 | A(1) | ○   | "N" |
| orgTrdNo | 원거래번호 | 취소 시, 원거래 번호 | AN(40) | ○   | "STFP\_PGCAnxca\_jt\_il0211129135810M1494620" |
| orgTrdDt | 원거래일자 | 취소 시, 원거래 일자 | N(8) | ○   | "20211231" |
| mixTrdNo | 복합결제 거래번호 | 복합결제 거래번호 | AN(40) | ○   | "STFP\_PGCAnxca\_jt\_il0211129135810M1494620" |
| mixTrdAmt | 복합결제 금액 | \*mixTrdNo 가 존재하는 경우에만 전달 | N(12) | ○   | "1000" |
| payAmt | 실 결제금액 | 거래금액에서 복합결제 금액을 제외한 결제 금액  <br>payAmt = trdAmt - mixTrdAmt  <br>\*mixTrdNo 가 존재하는 경우에만 전달 | N(12) | ○   | "1000" |
| cnclType | 취소거래타입 | 00:전체 취소, 10:부분 취소 | N(2) | ○   | "00" |
| mchtParam | 상점예약필드 | 상점에서 이용하는 추가 정보 필드로 전달한 값이 그대로 반환됩니다. | AHN(4000) | ○   | "name=HongGilDong&age=25" |
| pktHash | 해쉬값 | SHA256 (거래상태코드+거래일자+거래시간+상점아이디+상점주문번호+거래금액+해쉬키) | AN(64) | ●   | "a2d6d597d55d7c9b689baa2e08c1ddf0ce71f4248c5b9b59fe61bfbf949543e1" |

가맹점에서 헥토파이낸셜로 응답을 전송합니다.

 
| 응답 (가맹점 → 헥토파이낸셜) |     |
| --- | --- |
| 성공시 | "OK" (대문자) |
| 실패시 | "FAIL" (대문자, FAIL로 응답시 명확한 실패로 인식합니다. 노티가 재전송 됩니다.) |
| 그 외 | 비정상 실패로 인식하여, 설정된 횟수만큼 노티 재발송 처리함. |

# 7\. 신용카드 WebView

## 7.1 APP SCHEME 설정

*   결제 요청시 가맹점 App Scheme 설정
    *   `appScheme` 파라미터에 스키마 이름을 명시(가맹점앱스키마이름://)합니다.
    *   외부 앱을 호출하는 경우, 외부 앱 종료 시 해당 App Scheme 로 제어가 넘어갑니다.
    *   카드사 앱 호출 후 다른 결제 수단 앱으로 전환 시, 해당 App Scheme을 추가하면 됩니다.

## 7.2 안드로이드

*   WebViewClient 클래스의 shouldOverrideUrlLoading 메소드 재정의
    *   앱카드, 백신앱 등 외부 앱을 호출할 때, 앱이 설치되어 있지 않은 경우 마켓으로 이동하여 설치하는 로직입니다.

```
private class TestWebViewClient extends WebViewClient {

@Override
public boolean shouldOverrideUrlLoading(WebView view, String url) {   
	if(url == null)
		return false;
		
	if((url.startsWith("http://") || url.startsWith("https://"))){
		view.loadUrl(url);
		return false;
	}else{
		Intent intent;
		try{
					
			intent = Intent.parseUri(url, Intent.URI_INTENT_SCHEME);
			Uri uri = Uri.parse(intent.getDataString());
			intent = new Intent(Intent.ACTION_VIEW, uri);
			startActivity(intent);
			return true;	
		}catch(URISyntaxException e1){
			e1.printStackTrace();
			return false;
		}catch(ActivityNotFoundException e2){
			if(url.startsWith("ispmobile://")){
	Uri marketUri = Uri.parse("market://details?id=kvp.jjy.MispAndroid320");
				Intent marketIntent = new Intent(Intent.ACTION_VIEW,marketUri);
				startActivity(marketIntent);
				return true;
			}else if(url.startsWith("kftc-bankpay://")){
				Uri marketUri = Uri.parse("market://details?id=com.kftc.bankpay.android");
				Intent marketIntent = new Intent(Intent.ACTION_VIEW,marketUri);
				startActivity(marketIntent);
				return true;
			}else{
				try {
				    String packagename = intent.getPackage();
					if (packagename != null) {
						Uri marketUri = Uri.parse("market://details?id=" + packagename);
						Intent marketIntent = new Intent(Intent.ACTION_VIEW, marketUri);
						startActivity(marketIntent);
						return true;
					}
				} catch (URISyntaxException e3) {
					e3.printStackTrace();
					return false;
				}
			}
		}
	}
	return false;
}
```

*   웹뷰 설정 및 자바스크립트 ALERT / CONFIRM 메소드 구현
    *   ※ 자바스크립트를 사용가능하도록 설정 필수
    *   ※ Local Storage 사용 설정 필수
    *   ※ 캐시 사용 설정 필수
    *   alert / confirm 를 인식하게 합니다.

```
public void onCreate(Bundle savedInstanceState) {
	...
	view.setWebChromeClient(new MyWebChromeClient());
	WebSettings set = view.getSettings();
	set.setJavaScriptEnabled(true);
	set.setCacheMode(WebSettings.LOAD_DEFAULT);
	set.setDomStorageEnabled(true);
	...
}

class MyWebChromeClient extends WebChromeClient {

@Override
public booleanon JsAlert(WebView view, String url, String message, final android.webkit.JsResult result) {
	new AlertDialog.Builder(MainActivity.this).setTitle("").setMessage(message)
		.setPositiveButton(android.R.string.ok, new AlertDialog.OnClickListener() {
			public void onClick(DialogInterface dialog, int which) {
				result.confirm();
            }
        }).setCancelable(false).create().show();
		return true;
    }

    @Override
    public boolean onJsConfirm(WebView view, String url, String message, final JsResult result) {
    	new AlertDialog.Builder(MainActivity.this).setTitle("").setMessage(message)
    		.setPositiveButton(android.R.string.ok, new DialogInterface.OnClickListener() {
    			public void onClick(DialogInterface dialog, int which) {
    				result.confirm();
    			}
        }).setNegativeButton(android.R.string.cancel, new 
        	DialogInterface.OnClickListener() {
        		public void onClick(DialogInterface dialog, int which) {
        			result.cancel();
        		}
        }).create().show();
    	return true;
    }
}
```

*   안드로이드 Lollipop 버전 이후 적용사항
    *   Insecurity 페이지 허용 및 Third Party Cookies

```
WebSettings settings = view.getSettings();
 
if(Build.VERSION.SDK_INT>= Build.VERSION_CODES.LOLLIPOP) {

   settings.setMixedContentMode(settings.MIXED_CONTENT_ALWAYS_ALLOW);
   CookieManager.cookieManager = CookieManager.getInstance();
   cookieManager.setAcceptCookie(true);
   cookieManager.setAcceptThirdPartyCookies(view,true);

}
```

*   주요 외부 앱리스트
    *   Schema 및 Package Name

  
| App | Scheme | Package Name |
| --- | --- | --- |
| ISP모바일 | ispmobile | kvp.jjy.MispAndroid320 |
| KBAPP카드 | kb-acp | com.kbcard.cxh.appcard |
| KB스타뱅킹 | kbbank | com.kbstar.kbbank |
| L.POINT |     | com.lottemembers.android |
| L.pay | lpayapp | com..lotte.lpay |
| LG페이 | callonlinepay | com.lge.lgpay |
| LiiV(국민은행) | liivbank | com.kbstar.liivbank |
| NHAPP카드 | nhappcardansimclick | nh.smart.mobilecard |
| NH올원페이 | nhallonepayansimclick | nh.smart.nhallonepay |
| PAYCO간편결제 | payco | com.nhnent.payapp |
| SSGPAY |     | com.ssg.serviceapp.android.egiftcertificate |
| V3  | ahnlabv3mobileplus | com.ahnlab.v3mobileplus |
| VG웹백신 |     | kr.co.shiftworks.vguardweb |
| mVaccine | mvaccinestart | com.TouchEn.mVaccine.webs |
| 계좌이체 | kftc-bankpay | com.kftc.bankpay.android |
| 네이버페이 |     | com.nhn.android.search |
| 롯데APP카드 | lotteappcard | com.lcacApp |
| 롯데모바일결제 | lottesmartpay | com.lotte.lottesmartpay |
| 리브Next | newliiv | com.kbstar.reboot |
| 삼성APP카드 | mpocket.online.ansimclick | kr.co.samsungcard.mpocket |
| 삼성페이 | samsungpay | com.samsung.android.spay |
| 삼성페이(미니) |     | com.samsung.android.spaylite |
| 신한페이판(공동인증서) |     | com.shinhancard.smartshinhan |
| 신한 SOL뱅크 |     | com.shinhan.sbanking |
| 신한APP카드 | shinhan-sr-ansimclick | com.shcard.smartpay |
| 신한 슈퍼 SOL |     | com.shinhan.smartcaremgr |
| 씨티공인인증서/스마트간편결제 | smartpay | kr.co.citibank.citimobile |
| 씨티모바일앱 | citimobile | kr.co.citibank.citimobile |
| 씨티앱공인인증서 | citicardapp | com.citibank.cardapp |
| 씨티앱스마트간편결제 | citispay | com.citibank.cardapp |
| 우리WON뱅킹 | wooribank | com.wooribank.smart.npib |
| 우리WON카드 | com.wooricard.smartapp | com.wooricard.smartapp |
| 우리앱카드 | wooripay | com.wooricard.wpay |
| 카카오페이 |     | com.kakao.talk |
| 코나김포페이 |     | gov.gimpo.gpay |
| 토스  | supertoss | viva.republica.toss |
| 티머니댐댐 |     | com.tmoney.nfc\_pay |
| 티머니인앱 |     | com.tmoney.inapp |
| 페이핀 | paypin | com.skp.android.paypin |
| 하나(모비페이) | cloudpay | com.hanaskcard.paycla |
| 하나멤버스 |     | kr.co.hanamembers.hmscustomer |
| 하나멤버스월렛 | hanawalletmembers | com.hanaskcard.paycla |
| 현대APP카드 | hdcardappcardansimclick | com.hyundaicard.appcard |
| 현대카드(공동인증서) |     | com.lumensoft.touchenappfree |
| 카카오뱅크 | kakaobank | com.kakaobank.channel |

## 7.3 IOS

*   URL Scheme 설정
    *   IOS 9 이상에서는 보안정책 강화로 plist 파일에 `LSApplicationQueriesSchemes key`에 App Schema를 등록해야 합니다.
    *   LSApplicationQueriesSchemes 등록리스트는 APP을 제공하는 금융사의 사정에 따라 추가 및 변경 될 수 있습니다.

 
| App | Scheme |
| --- | --- |
| ISP 모바일 | ispmobile |
| KB APP 카드 | kb-acp |
| LiiV(국민은행) | liivbank |
| 리브 Next | newliiv |
| KB스타뱅킹 | kbbank |
| 롯데 APP 카드 | lotteappcard |
| 롯데 스마트 페이 | lottesmartpay |
| 현대 APP 카드 | hdcardappcardansimclick |
| 현대 공인인증 앱 | smhyundaiansimclick |
| 삼성APP카드 | mpocket.online.ansimclick |
| 삼성 공인인증 앱 | scardcertiapp |
| 신한APP카드 | shinhan-sr-ansimclick |
| 신한 공인인증 앱 | smshinhanansimclick |
| NH APP카드 | nhappcardansimclick |
| NH 올원페이 | nhallonepayansimclick |
| NH 공인인증 앱 | nonghyupcardansimclick |
| 하나(모비페이) | cloudpay |
| 씨티 APP 카드 | citispay |
| 씨티 공인인증 앱 | citicardappkr |
| 씨티공인인증서/스마트간편결제(신규) | citimobileapp |
| mVaccine | NA  |
| 계좌이체 | kftc-bankpay |
| 페이핀 | paypin |
| PAYCO 간편결제 | payco, paycoapplogin (2개 모두) |
| 시럽 APP카드 | tswansimclick |
| 뱅크월렛 | bankwallet |
| 은련카드 | uppay |
| 하나카드 | Hanaskcardmobileportal |
| LG페이 | Callonlinepay |
| L.pay | Lpayapp |
| 우리앱카드 | Wooripay |
| 하나멤버스월렛 | hanawalletmembers |
| 우리WON카드 | com.wooricard.wcard |
| 하나모아사인 | hanamopmoasign |
| 우리WON뱅킹 | NewSmartPib |
| Liiv(KB국민은행) | liivbank |
| 토스  | supertoss |
| 카카오뱅크 | kakaobank |

*   plist 예

```
<key>LSApplicationQueriesSchemes</key>
<array>
       <string>ispmobile</string>
       <string>hdcardappcardansimclick</string>
       <string>smhyundaiansimclick</string>
       <string>shinhan-sr-ansimclick</string>
       ...
</array>
```

 

*   쿠키허용
    *   IOS6 이상에서 Safari의 쿠키 기본설정이 허용된 것으로 바뀌어 세션만료 오류가 발생할 수 있습니다. 아래 코드를 적용하여 쿠키를 항상 허용으로 설정합니다.

```
(BOOL)application:(UIApplication *)application 
didFinishLaunchingWithOptions:(NSDictionary  *)launchOptions
{ 
	[[NSHTTPCookieStoragesharedHTTPCookieStorage]  
	setCookieAcceptPolicy:NSHTTPCookieAcceptPolicyAlways];   
    ... 
    return YES; 
} 
```

# 8\. 신용카드 결제 API (Non-UI)

## 8.1 결제 API 요청 전문 (빌키 발급 포함)

  
※ 구인증 : 카드번호, 유효기간(yyMM), 식별번호, 카드비밀번호로 결제 요청  
※ 비인증 : 카드번호, 유효기간(yyMM)으로 결제 요청  
※ 빌키(자동결제 키) 발급 : 상점 아이디 설정에 따라 빌키를 응답 값으로 내려 드리고 있으며, 빌키를 따로 저장 하였다가 결제가 필요할 경우 빌키 결제로 요청 주시길 바랍니다. 상점 아이디에 빌키 발급 설정은 영업 담당자를 통해 요청 주시기 바랍니다.  
  
가맹점 서버에서 헥토파이낸셜측으로 요청하는 컬럼을 다음과 같이 정의합니다.

      
| 파라미터 |     | 이름  | 설명  | 타입(길이) | 필수  | 비고  |
| --- | --- | --- | --- | --- | --- | --- |
| params | mchtId | 상점아이디 | 헥토파이낸셜에서 부여하는 고유 상점아이디  <br>nxca\_ks\_gu:구인증  <br>nxca\_jt\_bi:비인증 | AN(12) | ●   | "nxca\_jt\_bi" |
| ver | 버전  | 전문의 버전 | AN(4) | ●   | "0A19"  <br>※ 고정값 |
| method | 결제수단 | 결제수단 | A(2) | ●   | "CA"  <br>※ 고정값 |
| bizType | 업무구분 | 업무 구분코드 | AN(2) | ●   | "B0"  <br>※ 고정값 |
| encCd | 암호화 구분 | 암호화 구분 코드 | N(2) | ●   | "23"  <br>※ 고정값 |
| mchtTrdNo | 상점주문번호 | 상점에서 생성하는 고유한 거래번호 | AN(100) | ●   | "ORDER20211231100000" |
| trdDt | 요청일자 | 현재 전문을 전송하는 일자(YYYYMMDD) | N(8) | ●   | "20211231" |
| trdTm | 요청시간 | 현재 전문을 전송하는 시간(HHMMSS) | N(6) | ●   | "100000" |
| mobileYn | 모바일 여부 | Y:모바일웹/앱, N:PC 또는 그 외 | A(1) | ○   | "N" |
| osType | OS 구분 | A:Android, I:IOS, W:windows, M:Mac, E:기타  <br>공백:확인불가 | A(1) | ○   | "W" |
| data | pktHash | hash데이터 | SHA256 방식으로 생성한 해쉬값  <br>\[[요청 전문 해쉬 코드](#item-1050)\] 참고 | AN(200) | ●   | "f395b6725a9a18f2563ce34f8bc76698051d27c05e5ba815f463f00429061c0c" |
| pmtprdNm | 상품명 | 결제상품명 | AHN(128) | ●   | "테스트상품" |
| mchtCustNm | 고객명 | 상점 고객명 | AHN(30) | ●   | "홍길동" |
| mchtCustId | 상점고객아이디 | 상점 고객아이디 | AHN(50) | ●   | "HongGilDong" |
| email | 이메일 | 상점 고객 이메일주소 | AN(60) | ○   | "HongGilDong@example.com" |
| cardNo | 카드번호 | 카드번호  <br>※AES 암호화 | N(16) | ●   | "1111222233334444" |
| vldDtMon | 유효기간(월) | 유효기간 MM  <br>※AES 암호화 | N(2) | ●   | "12" |
| vldDtYear | 유효기간(년) | 유효기간 YY  <br>※AES 암호화 | N(2) | ●   | "24" |
| idntNo  <br>※ 구인증만 사용 | 식별번호 | 생년월일 6자리 또는 사업자 번호 10자리  <br>※AES 암호화 | N(10) | ●   | "991231" |
| cardPwd  <br>※ 구인증만 사용 | 카드비밀번호 | 카드비밀번호 앞 2자리  <br>※AES 암호화  <br>※ 구인 증 결제시에만 사용합니다. | N(2) | ●   | "00" |
| instmtMon | 할부개월수 | 할부개월수 2자리 | N(2) | ●   | "00" |
| crcCd | 통화구분 | 통화구분 | A(3) | ●   | "KRW" ※국내결제  <br>"USD"  ※해외결제 |
| taxTypeCd | 세금유형 | N : 과세, Y : 면세, G : 복합과세  <br>공백일 경우 상점 설정에 따름 | A(1) | ○   | "N" |
| trdAmt | 거래금액 | 거래금액  <br>※AES 암호화 | N(12) | ●   | "1000" ※국내결제  <br>"150"   ※해외결제  <br>ex \[1.50$\] => 정수표기 \[150\] |
| taxAmt | 과세금액 | 거래금액 중 과세금액  <br>(복합과세일 경우 필수)  <br>※AES 암호화 | N(12) | ○   | "909" |
| vatAmt | 부가세금액 | 거래금액 중 부가세금액  <br>(복합과세일 경우 필수)  <br>※AES 암호화 | N(12) | ○   | "91" |
| taxFreeAmt | 비과세금액 | 거래금액 중 비과세금액  <br>(복합과세일 경우 필수)  <br>※AES 암호화 | N(12) | ○   | "0" |
| svcAmt | 봉사료 | 신용카드 봉사료  <br>※AES 암호화 | N(12) | ○   | "10" |
| notiUrl | 결과처리URL | 결제완료후, 헥토파이낸셜에서 상점으로 전달하는  <br>노티(결과통보)를 수신하는Callback URL 작성 | AN(250) | ○   | "https://example.com/notiUrl" |
| mchtParam | 상점예약필드 | 기타 주문 정보를 입력하는 상점 예약 필드 | AHN(4000) | ○   | "name=HongGilDong&age=25" |

## 8.2 요청 전문 해쉬 코드

 
| 항목  | 조합 필드 |
| --- | --- |
| pktHash | 거래일자 + 거래시간 + 상점아이디 + 상점주문번호 + 거래금액(평문) + 해쉬키 |

## 8.3 결제 API 응답 전문 (빌키 발급 포함)

      
| 파라미터 |     | 이름  | 설명  | 타입(길이) | 필수  | 비고  |
| --- | --- | --- | --- | --- | --- | --- |
| params | mchtId | 상점아이디 | 헥토파이낸셜에서 부여하는 고유 상점아이디 | AN(12) | ●   | "nxca\_jt\_bi" |
| ver | 버전  | 전문의 버전 | AN(4) | ●   | "0A19"  <br>※ 고정값 |
| method | 결제수단 | 결제수단 | A(2) | ●   | "CA"  <br>※ 고정값 |
| bizType | 업무구분 | 업무 구분코드 | AN(2) | ●   | "B0"  <br>※ 고정값 |
| encCd | 암호화 구분 | 암호화 구분 코드 | N(2) | ●   | "23"  <br>※ 고정값 |
| mchtTrdNo | 상점주문번호 | 상점에서 생성하는 고유한 주문번호 | AN(100) | ●   | "ORDER20211231100000" |
| trdNo | 헥토파이낸셜거래번호 | 헥토파이낸셜에서 발급한 고유한 거래번호 | AN(40) | ●   | "STFP\_PGCAnxca\_jt\_il0211129135810M1494620" |
| trdDt | 요청일자 | 현재 전문을 전송하는 일자(YYYYMMDD) | N(8) | ●   | "20211231" |
| trdTm | 요청시간 | 현재 전문을 전송하는 시간(HHMMSS) | N(6) | ●   | "100000" |
| outStatCd | 거래상태 | 거래상태코드(성공/실패)  <br>0021:성공  <br>0031:실패 | AN(4) | ●   | "0021" |
| outRsltCd | 거절코드 | 거래상태가 "0031"일 경우, 상세 코드 전달  <br>\[[거절 코드 표](#item-544)\] 참고 | AN(4) | ●   | "0000" |
| outRsltMsg | 결과메세지 | 결과 메세지 전달  <br>URL Encoding, UTF-8 | AHN(200) | ●   | "정상적으로 처리되었습니다." |
| data | pktHash | 해쉬값 | 요청시, hash 값 그대로 return | AN(64) | ●   |     |
| trdAmt | 거래금액 | 거래금액  <br>※AES 암호화 | N(12) | ●   | "1000" ※국내결제  <br>"150"   ※해외결제  <br>ex \[1.50$\] => 정수표기 \[150\] |
| billKey | 빌키  | 2회차 결제시 사용되는 빌키  <br>※ 빌키 서비스 이용 상점에 한하여 제공됩니다. | AN(50) | ○   | "SBILL\_0123456789" |
| cardNo | 카드번호 | 마스킹 된 카드번호를 return합니다.  <br>※ 기본적으로 제공되지 않으며, 특정 상점에 한하여 제공됩니다. 사업부에 문의 부탁드립니다. | N(16) | ○   | "111122xxxxxx4444" |
| vldDtMon | 유효기간(월) | 유효기간 MM  <br>※ 빌키 서비스 이용 상점에 한하여 제공됩니다. | N(2) | ○   | "12" |
| vldDtYear | 유효기간(년) | 유효기간 YY  <br>※ 빌키 서비스 이용 상점에 한하여 제공됩니다. | N(2) | ○   | "24" |
| issrId | 발급사아이디 | 카드발급사 코드  <br>\[[신용카드 식별자](#item-545)\] 참고 | AN(4) | ●   | "NHC" |
| cardNm | 카드사명 | 카드사 명  <br>\[[신용카드 식별자](#item-545)\] 참고 | AHN(20) | ●   | "NH 농협" |
| cardKind | 카드종류명 | 카드 종류  <br>\[[신용카드 식별자](#item-545)\] 참고 | AHN(50) | ●   | "NH 체크카드" |
| ninstmtTypeCd | 무이자할부타입 | Y:무이자(부분,상점)  <br>N:일반할부, 일시불 | A(1) | ●   | "N" |
| instmtMon | 할부개월수 | 요청 시 값 그대로 return | N(2) | ○   | "00" |
| apprNo | 승인번호 | 카드 승인번호 | N(15) | ●   | "30001234" |

## 8.4 응답 전문 해쉬 코드

 
| 항목  | 조합 필드 |
| --- | --- |
| pktHash | 거래상태코드 + 요청일자 + 요청시간 + 상점아이디 + 상점주문번호 + 거래금액 + 해쉬키 |

## 8.5 빌키 발급 API 요청 전문

※ 결제 하지 않고 빌키 발급  
가맹점 서버에서 헥토파이낸셜측으로 요청하는 컬럼을 다음과 같이 정의합니다.

      
| 파라미터 |     | 이름  | 설명  | 타입(길이) | 필수  | 비고  |
| --- | --- | --- | --- | --- | --- | --- |
| params | mchtId | 상점아이디 | 헥토파이낸셜에서 부여하는 고유 상점아이디 | AN(12) | ●   | "nxca\_ks\_gu" |
| ver | 버전  | 전문의 버전 | AN(4) | ●   | "0A19"  <br>※ 고정값 |
| method | 결제수단 | 결제수단 | A(2) | ●   | "CA"  <br>※ 고정값 |
| bizType | 업무구분 | 업무 구분코드 | AN(2) | ●   | "A4"  <br>※ 고정값 |
| encCd | 암호화 구분 | 암호화 구분 코드 | N(2) | ●   | "23"  <br>※ 고정값 |
| mchtTrdNo | 상점주문번호 | 상점에서 생성하는 고유한 주문번호 | AN(100) | ●   | "PG\_API20220920131039" |
| trdDt | 요청일자 | 현재 전문을 전송하는 일자(YYYYMMDD) | N(8) | ●   | "20220920" |
| trdTm | 요청시간 | 현재 전문을 전송하는 시간(HHMMSS) | N(6) | ●   | "131039" |
| mobileYn | 모바일 여부 | Y:모바일웹/앱, N:PC 또는 그 외 | A(1) | ○   | "N" |
| osType | OS 구분 | A:Android, I:IOS, W:windows, M:Mac, E:기타  <br>공백:확인불가 | A(1) | ○   | "W" |
| data | pktHash | hash값 | SHA256 방식으로 생성한 해쉬값  <br>\[[요청 전문 해쉬 코드](#item-1131)\] 참고 | AN(64) | ●   | "3bf1295695eb0e081f7900dfcbfcb225887d8fb07322d54c3dba72a2726bf55d" |
| cardNo | 카드번호 | 카드번호, 숫자만  <br>※AES 암호화 | N(128) | ●   | "522112\*\*\*\*\*\*1621" |
| idntNo | 식별번호 | 생년월일6자리  or 사업자번호10자리  <br>※AES 암호화 | N(64) | ●   | "620817" |
| vldDtMon | 유효기간(월) | 카드 유효기간(월), 숫자만  <br>※AES 암호화 | N(24) | ●   | "11" |
| vldDtYear | 유효기간(년) | 카드 유효기간(년), 숫자만  <br>※AES 암호화 | N(24) | ●   | "11" |
| cardPwd | 카드비밀번호 | 카드 비밀번호 앞2자리  <br>※AES 암호화 | N(24) | ●   | "11" |
| mchtCustNm | 고객명 | 고객명(한글포함가능) | AHN(30) | ○   | "홍길동" |
| mchtCustId | 고객아이디 | 고객아이디(한글포함불가) | AHN(50) | ○   | "HongGilDong" |
| keyRegYn | 빌키발급요청여부 | 인증후 빌키발급여부(Y, N) | A(1) | ●   | "Y" |

## 8.6 요청 전문 해쉬 코드

 
| 항목  | 조합 필드 |
| --- | --- |
| pktHash | 요청일자 + 요청시간 + 상점아이디 + 상점주문번호 + "0" + 해쉬키 |

## 8.7 빌키 발급 API 응답 전문

      
| 파라미터 |     | 이름  | 설명  | 타입(길이) | 필수  | 비고  |
| --- | --- | --- | --- | --- | --- | --- |
| params | mchtId | 상점아이디 | 헥토파이낸셜에서 부여하는 고유 상점아이디 | AN(12) | ●   | "nxca\_ks\_gu" |
| ver | 버전  | 전문의 버전 | AN(4) | ●   | "0A19"  <br>※ 고정값 |
| method | 결제수단 | 결제수단 | A(2) | ●   | "CA"  <br>※ 고정값 |
| bizType | 업무구분 | 업무 구분코드 | AN(2) | ●   | "A4"  <br>※ 고정값 |
| encCd | 암호화 구분 | 암호화 구분 코드 | N(2) | ●   | "23"  <br>※ 고정값 |
| mchtTrdNo | 상점주문번호 | 상점에서 생성하는 고유한 주문번호 | AN(100) | ●   | "PG\_API20220920131039" |
| trdNo | 헥토파이낸셜 거래번호 | 헥토파이낸셜에서 생성하는 고유한 거래번호 | AN(40) | ●   | "STFP\_PGCAnxca\_ks\_gu0220921093117M1260999" |
| trdDt | 거래일자 | 현재 전문을 전송하는 일자(YYYYMMDD) | N(8) | ●   | "20220921" |
| trdTm | 거래시간 | 현재 전문을 전송하는 시간(HHMMSS) | N(6) | ●   | "093117" |
| outStatCd | 거래상태 | 0021:성공, 0031:실패  <br>(성공건 확인: 거래상태=0021 + 결과코드=0000) | N(4) | ●   | "0021" |
| outRsltCd | 결과코드 | 결과코드. 성공 0000, 그 외 \[[거절 코드 표\]](https://develop.sbsvc.online/16/onlineDocList.do#item-544) 참고 | N(4) | ●   | "0000" |
| outRsltMsg | 결과메시지 | 결과 메시지 | AHN(200) | ●   | "정상처리되었습니다" |
| data | pktHash | hash데이터 | SHA256 방식으로 생성한 해쉬값 | AN(64) | ●   | "07d36ed4ef2a773829feca675b01e3f16db40f90b3895c6f8d85e6d0e7c1d583" |
| cardNo | 카드번호 | 카드번호 | N(128) | ○   | "522112\*\*\*\*\*\*1621" |
| issrId | 발급사 아이디 | 카드발급사 식별자  <br>\[[신용카드 식별자](https://develop.sbsvc.online/16/onlineDocList.do#item-545)\] 참고 | A(64) | ○   | "HDC" |
| cardNm | 카드사 명 | 카드사 명  <br>\[[신용카드 식별자](https://develop.sbsvc.online/16/onlineDocList.do#item-545)\] 참고 | AH(20) | ○   | "현대" |
| cardKind | 카드종류 명 | 카드 종류  <br>\[[신용카드 식별자](https://develop.sbsvc.online/16/onlineDocList.do#item-545)\] 참고 | AN(50) | ○   | "현대마스타개인" |
| billKey | 빌키  | 발급요청 Y일때 빌키응답 | AN(40) | ○   | "SBILL\_PGCAnxca\_ks\_gu20222609990921093117" |

## 8.8 응답 전문 해쉬 코드

 
| 항목  | 조합 필드 |
| --- | --- |
| pktHash | 거래상태코드 + 요청일자 + 요청시간 + 상점아이디 + 상점주문번호 + "0" + 해쉬키 |

# 9\. 신용카드 빌키 결제 API(Non-UI)

*   신용카드 결제 API 또는 빌키 발급 API를 통해 전달받은 빌키로 결제를 하는 API입니다.
*   빌키 서비스는 영업 담당자를 통해 별도 신청이 필요합니다.

## 9.1 요청 전문 (가맹점 → 헥토파이낸셜)

      
| 파라미터 |     | 이름  | 설명  | 타입(길이) | 필수  | 비고  |
| --- | --- | --- | --- | --- | --- | --- |
| params | mchtId | 상점아이디 | 헥토파이낸셜에서 부여하는 고유 상점아이디  <br>nxca\_ks\_gu:구인증  <br>nxca\_jt\_bi:비인증 | AN(12) | ●   | "nxca\_jt\_bi" |
| ver | 버전  | 전문의 버전 | AN(4) | ●   | "0A19"  <br>※ 고정값 |
| method | 결제수단 | 결제수단 | A(2) | ●   | "CA"  <br>※ 고정값 |
| bizType | 업무구분 | 업무 구분코드 | AN(2) | ●   | "B0"  <br>※ 고정값 |
| encCd | 암호화 구분 | 암호화 구분 코드 | N(2) | ●   | "23"  <br>※ 고정값 |
| mchtTrdNo | 상점주문번호 | 상점에서 생성하는 고유한 주문번호 | AN(100) | ●   | "ORDER20211231100000" |
| trdDt | 요청일자 | 현재 전문을 전송하는 일자(YYYYMMDD) | N(8) | ●   | "20211231" |
| trdTm | 요청시간 | 현재 전문을 전송하는 시간(HHMMSS) | N(6) | ●   | "100000" |
| mobileYn | 모바일 여부 | Y:모바일웹/앱, N:PC 또는 그 외 | A(1) | ○   | "N" |
| osType | OS 구분 | A:Android, I:IOS, W:windows, M:Mac, E:기타  <br>공백:확인불가 | A(1) | ○   | "W" |
| data | pktHash | hash데이터 | SHA256 방식으로 생성한 해쉬값  <br>\[[요청 전문 해쉬 코드](#item-1053)\] 참고 | AN(200) | ●   | "f395b6725a9a18f2563ce34f8bc76698051d27c05e5ba815f463f00429061c0c" |
| pmtprdNm | 상품명 | 결제상품명 | AHN(128) | ●   | "테스트상품" |
| mchtCustNm | 고객명 | 상점 고객명 | AHN(30) | ●   | "홍길동" |
| mchtCustId | 상점고객아이디 | 상점 고객아이디 | AHN(50) | ●   | "HongGilDong" |
| email | 이메일 | 상점 고객 이메일주소 | AN(60) | ○   | "HongGilDong@example.com" |
| billKey | 빌키  | 1회차 결제시 발급받았던 빌키 | AN(50) | ●   | "SBILL\_0123456789" |
| instmtMon | 할부개월수 | 할부개월수 2자리 | N(2) | ●   | "00" |
| crcCd | 통화구분 | 통화구분 | A(3) | ●   | "KRW"  <br>※ 국내결제  <br>"USD"    <br>※ 해외결제 |
| taxTypeCd | 세금유형 | N : 과세, Y : 면세, G : 복합과세  <br>공백일 경우 상점 설정에 따름 | A(1) | ○   | "N" |
| trdAmt | 거래금액 | 거래금액  <br>※AES 암호화 | N(12) | ●   | "1000" ※ 국내결제  <br>"150"   ※ 해외결제  <br>ex \[1.50$\] => 정수표기 \[150\] |
| taxAmt | 과세금액 | 거래금액 중 과세금액  <br>(복합과세일 경우 필수)  <br>※AES 암호화 | N(12) | ○   | "909" |
| vatAmt | 부가세금액 | 거래금액 중 부가세금액  <br>(복합과세일 경우 필수)  <br>※AES 암호화 | N(12) | ○   | "91" |
| taxFreeAmt | 비과세금액 | 거래금액 중 비과세금액  <br>(복합과세일 경우 필수)  <br>※AES 암호화 | N(12) | ○   | "0" |
| svcAmt | 봉사료 | 신용카드 봉사료  <br>※AES 암호화 | N(12) | ○   | "10" |
| mchtParam | 상점예약필드 | 기타 주문 정보를 입력하는 상점 예약 필드 | AHN(4000) | ○   | "name=HongGilDong&age=25" |

## 9.2 요청 전문 해쉬 코드

 
| 항목  | 조합 필드 |
| --- | --- |
| pktHash | 거래일자 + 거래시간 + 상점아이디 + 상점주문번호 + 거래금액(평문) + 해쉬키 |

## 9.3 응답 전문 (헥토파이낸셜 → 가맹점)

      
| 파라미터 |     | 이름  | 설명  | 타입(길이) | 필수  | 비고  |
| --- | --- | --- | --- | --- | --- | --- |
| params | mchtId | 상점아이디 | 헥토파이낸셜에서 부여하는 고유 상점아이디 | AN(12) | ●   | "nxca\_jt\_bi" |
| ver | 버전  | 전문의 버전 | AN(4) | ●   | "0A19"  <br>※ 고정값 |
| method | 결제수단 | 결제수단 | A(2) | ●   | "CA"  <br>※ 고정값 |
| bizType | 업무구분 | 업무 구분코드 | AN(2) | ●   | "B0"  <br>※ 고정값 |
| encCd | 암호화 구분 | 암호화 구분 코드 | N(2) | ●   | "23"  <br>※ 고정값 |
| mchtTrdNo | 상점주문번호 | 상점에서 생성하는 고유한 주문번호 | AN(100) | ●   | "ORDER20211231100000" |
| trdNo | 헥토파이낸셜거래번호 | 헥토파이낸셜에서 발급한 고유한 거래번호 | AN(40) | ●   | "STFP\_PGCAnxca\_jt\_il0211129135810M1494620" |
| trdDt | 요청일자 | 현재 전문을 전송하는 일자(YYYYMMDD) | N(8) | ●   | "20211231" |
| trdTm | 요청시간 | 현재 전문을 전송하는 시간(HHMMSS) | N(6) | ●   | "100000" |
| outStatCd | 거래상태 | 거래상태코드(성공/실패)  <br>0021:성공  <br>0031:실패 | AN(4) | ●   | "0021" |
| outRsltCd | 거절코드 | 거래상태가 "0031"일 경우, 상세 코드 전달  <br>\[[거절 코드 표](#item-544)\] 참고 | AN(4) | ●   | "0000" |
| outRsltMsg | 결과메세지 | 결과 메세지 전달  <br>URL Encoding, UTF-8 | AHN(200) | ●   | "정상적으로 처리되었습니다." |
| data | pktHash | 해쉬값 | 요청시, hash 값 그대로 return | AN(64) | ●   |     |
| trdAmt | 거래금액 | 거래금액  <br>※AES 암호화 | N(12) | ●   | "1000" |
| billKey | 빌키  | 요청 시 값 그대로 return | AN(50) | ●   | "SBILL\_0123456789" |
| cardNo | 카드번호 | 마스킹 된 카드번호를 return합니다.  <br>※ 기본적으로 제공되지 않으며, 특정 상점에 한하여 제공됩니다. 사업부에 문의 부탁드립니다. | N(16) | ○   | "111122xxxxxx4444" |
| vldDtMon | 유효기간(월) | 유효기간 MM  <br>※ 빌키 서비스 이용 상점에 한하여 제공됩니다. | N(2) | ○   | "12" |
| vldDtYear | 유효기간(년) | 유효기간 YY  <br>※ 빌키 서비스 이용 상점에 한하여 제공됩니다. | N(2) | ○   | "24" |
| issrId | 발급사아이디 | 카드발급사 식별자  <br>\[[신용카드 식별자](#item-545)\] 참고 | AN(4) | ●   | "NHC" |
| cardNm | 카드사명 | 카드사 명  <br>\[[신용카드 식별자](#item-545)\] 참고 | AHN(20) | ●   | "NH 농협" |
| cardKind | 카드종류명 | 카드 종류  <br>\[[신용카드 식별자](#item-545)\] 참고 | AHN(50) | ●   | "NH 체크카드" |
| ninstmtTypeCd | 무이자할부타입 | Y:무이자(부분,상점)  <br>N:일반할부, 일시불 | A(1) | ●   | "N" |
| instmtMon | 할부개월수 | 요청 시 값 그대로 return | N(2) | ○   | "00" |
| apprNo | 승인번호 | 카드 승인번호 | N(15) | ●   | "30001234" |

## 9.4 응답 전문 해쉬 코드

 
| 항목  | 조합 필드 |
| --- | --- |
| pktHash | 거래상태코드 + 요청일자 + 요청시간 + 상점아이디 + 상점주문번호 + 거래금액 + 해쉬키 |

# 10\. 신용카드 빌키 삭제 API (Non-UI)

## 10.1 요청 전문 (가맹점 → 헥토파이낸셜)

      
| 파라미터 |     | 이름  | 설명  | 타입(길이) | 필수  | 비고  |
| --- | --- | --- | --- | --- | --- | --- |
| params | mchtId | 상점아이디 | 헥토파이낸셜에서 부여하는 고유 상점아이디  <br>nxca\_jt\_bi:비인증  <br>nxca\_ks\_gu:구인증 | AN(12) | ●   | "nxca\_jt\_bi" |
| ver | 버전  | 전문의 버전 | AN(4) | ●   | "0A19"  <br>※ 고정값 |
| method | 결제수단 | 결제수단 | A(2) | ●   | "CA"  <br>※ 고정값 |
| bizType | 업무구분 | 업무 구분코드 | AN(2) | ●   | "A1"  <br>※ 고정값 |
| encCd | 암호화 구분 | 암호화 구분 코드 | N(2) | ●   | "23"  <br>※ 고정값 |
| mchtTrdNo | 상점주문번호 | 상점에서 생성하는 고유한 주문번호 | AN(100) | ●   | "ORDER20211231100000" |
| trdDt | 요청일자 | 현재 전문을 전송하는 일자(YYYYMMDD) | N(8) | ●   | "20211231" |
| trdTm | 요청시간 | 현재 전문을 전송하는 시간(HHMMSS) | N(6) | ●   | "100000" |
| mobileYn | 모바일 여부 | Y:모바일웹/앱, N:PC 또는 그 외 | A(1) | ○   | "N" |
| osType | OS 구분 | A:Android, I:IOS, W:windows, M:Mac, E:기타  <br>공백:확인불가 | A(1) | ○   | "W" |
| data | pktHash | hash데이터 | SHA256 방식으로 생성한 해쉬값  <br>\[[요청 전문 해쉬 코드](#item-1056)\] 참고 | AN(200) | ●   | "f395b6725a9a18f2563ce34f8bc76698051d27c05e5ba815f463f00429061c0c" |
| billKey | 빌키  | 1회차 응답으로 발급받은 빌키 | AN(50) | ●   | "SBILL\_0123456789" |
| etcInfo | 해지사유 | 해지사유코드 | AN(12) | ○   | ""  |

## 10.2 요청 전문 해쉬 코드

 
| 항목  | 조합 필드 |
| --- | --- |
| pktHash | 거래일자 + 거래시간 + 상점아이디 + 상점주문번호 + "0" + 해쉬키 |

## 10.3 응답 전문 (헥토파이낸셜 → 가맹점)

      
| 파라미터 |     | 이름  | 설명  | 타입(길이) | 필수  | 비고  |
| --- | --- | --- | --- | --- | --- | --- |
| params | mchtId | 상점아이디 | 헥토파이낸셜에서 부여하는 고유 상점아이디 | AN(12) | ●   | "nxca\_jt\_bi" |
| ver | 버전  | 전문의 버전 | AN(4) | ●   | "0A19"  <br>※ 고정값 |
| method | 결제수단 | 결제수단 | A(2) | ●   | "CA"  <br>※ 고정값 |
| bizType | 업무구분 | 업무 구분코드 | AN(2) | ●   | "A1"  <br>※ 고정값 |
| encCd | 암호화 구분 | 암호화 구분 코드 | N(2) | ●   | "23"  <br>※ 고정값 |
| mchtTrdNo | 상점주문번호 | 상점에서 생성하는 고유한 주문번호 | AN(100) | ●   | "ORDER20211231100000" |
| trdNo | 헥토파이낸셜거래번호 | 헥토파이낸셜에서 발급한 고유한 거래번호 | AN(40) | ●   | "STFP\_PGCAnxca\_jt\_il0211129135810M1494620" |
| trdDt | 요청일자 | 현재 전문을 전송하는 일자(YYYYMMDD) | N(8) | ●   | "20211231" |
| trdTm | 요청시간 | 현재 전문을 전송하는 시간(HHMMSS) | N(6) | ●   | "100000" |
| outStatCd | 거래상태 | 거래상태코드(성공/실패)  <br>0021:성공  <br>0031:실패 | AN(4) | ●   | "0021" |
| outRsltCd | 거절코드 | 거래상태가 "0031"일 경우, 상세 코드 전달  <br>\[[거절 코드 표](#item-544)\] 참고 | AN(4) | ●   | "0000" |
| outRsltMsg | 결과메세지 | 결과 메세지 전달  <br>URL Encoding, UTF-8 | AHN(200) | ●   | "정상적으로 처리되었습니다." |
| data | pktHash | 해쉬값 | 요청시, hash 값 그대로 return | AN(64) | ●   |     |
| billKey | 빌키  | 요청시, 값 그대로 return | AN(50) | ●   | "SBILL\_0123456789" |

## 10.4 응답 전문 해쉬 코드

 
| 항목  | 조합 필드 |
| --- | --- |
| pktHash | 거래상태코드 + 요청일자 + 요청시간 + 상점아이디 + 상점주문번호 + 거래금액 + 해쉬키 |

# 11\. 신용카드 취소 (Non-UI)

## 11.1 요청 전문 (가맹점 → 헥토파이낸셜)

*   API URI
    *   테스트계 : https://tbgw.settlebank.co.kr/spay/APICancel.do
    *   운영계 : https://gw.settlebank.co.kr/spay/APICancel.do

  
가맹점 서버에서 헥토파이낸셜측으로 요청하는 컬럼을 다음과 같이 정의합니다.

      
| 파라미터 |     | 이름  | 설명  | 타입(길이) | 필수  | 비고  |
| --- | --- | --- | --- | --- | --- | --- |
| params | mchtId | 상점아이디 | 헥토파이낸셜에서 부여하는 고유 상점아이디  <br>nxca\_jt\_il:인증  <br>nxca\_jt\_bi:비인증  <br>nxca\_ks\_gu:구인증  <br>nxca\_ab\_bi:영문외화 비인증 | AN(12) | ●   | "nxca\_jt\_il" |
| ver | 버전  | 전문의 버전 | AN(4) | ●   | "0A19"  <br>※ 고정값 |
| method | 결제수단 | 결제수단 | A(2) | ●   | "CA"  <br>※ 고정값 |
| bizType | 업무구분 | 업무 구분코드 | AN(2) | ●   | "C0"  <br>※ 고정값 |
| encCd | 암호화 구분 | 암호화 구분 코드 | N(2) | ●   | "23"  <br>※ 고정값 |
| mchtTrdNo | 상점주문번호 | 상점에서 생성하는 고유한 주문번호 | AN(100) | ●   | "ORDER20211231100000" |
| trdDt | 취소요청일자 | 현재 전문을 전송하는 일자(YYYYMMDD) | N(8) | ●   | "20211231" |
| trdTm | 취소요청시간 | 현재 전문을 전송하는 시간(HHMMSS) | N(6) | ●   | "100000" |
| mobileYn | 모바일 여부 | Y:모바일웹/앱, N:PC 또는 그 외 | A(1) | ○   | "N" |
| osType | OS 구분 | A:Android, I:IOS, W:windows, M:Mac, E:기타, 공백:확인불가 | A(1) | ○   | "W" |
| data | pktHash | hash데이터 | SHA256 방식으로 생성한 해쉬값  <br>\[[요청 전문 해쉬 코드](#item-441)\] 참고 | AN(200) | ●   | "f395b6725a9a18f2563ce34f8bc76698051d27c05e5ba815f463f00429061c0c" |
| orgTrdNo | 원거래번호 | 결제 시, 헥토파이낸셜에서 발급한 거래번호 | AN(40) | ●   | "STFP\_PGCAnxca\_jt\_il0211129135810M1494620" |
| crcCd | 통화구분 | 통화 구분 값 | A(3) | ●   | "KRW" ※국내결제  <br>"USD"  ※해외결제 |
| cnclOrd | 취소회차 | 001부터 시작. 부분취소 2회차의 경우 002 | N(3) | ●   | "001" |
| taxTypeCd | 면세여부 | Y:면세, N:과세, G:복합과세. 공백일 경우 상점 기본 정보에 따름. | A(1) | ○   | "N" |
| cnclAmt | 취소금액 | 취소금액  <br>※ AES 암호화 | N(12) | ●   | "1000" ※국내결제  <br>"150"   ※해외결제  <br>ex \[1.50$\] => 정수표기 \[150\] |
| taxAmt | 과세금액 | 취소금액 중 과세금액(복합과세인 경우 필수)  <br>※ AES 암호화 | N(12) | ○   | "909" |
| vatAmt | 부가세금액 | 취소금액 중 부가세금액(복합과세인 경우 필수)  <br>※ AES 암호화 | N(12) | ○   | "91" |
| taxFreeAmt | 비과세금액 | 취소금액 중 면세금액(복합과세인 경우 필수)  <br>※ AES 암호화 | N(12) | ○   | "0" |
| svcAmt | 봉사료 | 취소금액 중 봉사료  <br>※ AES 암호화 | N(12) | ○   | "0" |
| cnclRsn | 취소사유내용 | 필요한 경우, 취소 사유 메세지 기재 | AHN(255) | ○   | "상품이 마음에 들지 않아서" |

## 11.2 요청 전문 해쉬 코드

 
| 항목  | 조합 필드 |
| --- | --- |
| pktHash | 취소요청일자 + 취소요청시간 + 상점아이디 + 상점주문번호 + 취소금액(평문) + 해쉬키 |

## 11.3 응답 전문 (헥토파이낸셜 → 가맹점)

헥토파이낸셜에서 가맹점측으로 응답하는 컬럼을 다음과 같이 정의합니다.

      
| 파라미터 |     | 이름  | 설명  | 타입(길이) | 필수  | 비고  |
| --- | --- | --- | --- | --- | --- | --- |
| params | mchtId | 상점아이디 | 헥토파이낸셜에서 부여하는 고유 상점아이디  <br>nxca\_jt\_il:인증  <br>nxca\_jt\_bi:비인증  <br>nxca\_ks\_gu:구인증 | AN(12) | ●   | "nxca\_jt\_il" |
| ver | 버전  | 전문의 버전 | AN(4) | ●   | "0A19"  <br>※ 고정값 |
| method | 결제수단 | 결제수단 | A(2) | ●   | "CA"  <br>※ 고정값 |
| bizType | 업무구분 | 업무 구분코드 | AN(2) | ●   | "C0"  <br>※ 고정값 |
| encCd | 암호화 구분 | 암호화 구분 코드 | N(2) | ●   | "23"  <br>※ 고정값 |
| mchtTrdNo | 상점주문번호 | 상점에서 생성하는 고유한 주문번호 | AN(100) | ●   | "ORDER20211231100000" |
| trdNo | 헥토파이낸셜 거래번호 | 헥토파이낸셜에서 생성하는 고유한 거래번호 | AN(40) | ●   | "STFP\_PGCAnxca\_jt\_il0211129135810M1494620" |
| trdDt | 취소요청일자 | 현재 전문을 전송하는 일자(YYYYMMDD) | N(8) | ●   | "20211231" |
| trdTm | 취소요청시간 | 현재 전문을 전송하는 시간(HHMMSS) | N(6) | ●   | "100000" |
| outStatCd | 거래상태 | 거래상태코드(성공/실패)  <br>0021:성공  <br>0031:실패 | AN(4) | ●   | "0021" |
| outRsltCd | 거절코드 | 거래상태가 "0031"일 경우, 상세 코드 전달  <br>\[[거절 코드 표](#item-544)\] 참고 | AN(4) | ●   | "0000" |
| outRsltMsg | 결과메세지 | 결과 메세지 전달  <br>URL Encoding, UTF-8 | AHN(200) | ●   | "정상적으로 처리되었습니다." |
| data | pktHash | 해쉬값 | 요청시, hash 값 그대로 return | AN(64) | ●   |     |
| orgTrdNo | 원거래번호 | 결제 시, 헥토파이낸셜에서 발급한 거래번호 | AN(40) | ●   | "STFP\_PGCAnxca\_jt\_il0211129135810M1494620" |
| cnclAmt | 취소금액 | 취소금액  <br>※ AES 암호화 | N(12) | ●   | "1000" ※국내결제  <br>"150"   ※해외결제  <br>ex \[1.50$\] => 정수표기 \[150\] |
| cardCnclAmt | 신용카드 취소금액 | 전체금액 중 신용카드 취소금액  <br>※ AES 암호화 | N(12) | ●   | "5000" |
| pntCnclAmt | 포인트 취소금액 | 전체금액 중 포인트 취소금액  <br>※ AES 암호화 | N(12) | ●   | "1000" |
| blcAmt | 취소가능잔액 | 취소성공시 거래번호 기준 남은 취소 가능잔액 리턴  <br>※ AES 암호화 | N(12) | ●   | "0" |

## 11.4 노티 전문 (헥토파이낸셜 → 가맹점)

※ \[[6.5 노티 전문](#item-773)\] 참고

