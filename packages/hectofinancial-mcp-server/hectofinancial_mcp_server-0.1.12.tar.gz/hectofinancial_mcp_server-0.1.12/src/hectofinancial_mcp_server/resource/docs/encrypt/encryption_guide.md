# 헥토파이낸셜 암호화 가이드

## 1. 개요

헥토파이낸셜의 모든 서비스에서 사용되는 암호화 방식과 테스트 환경 설정에 대한 종합 가이드입니다.

### 1.1 목적
- 암호화 방식 통일성 확보
- 테스트 환경 vs 운영 환경 구분
- 보안 요구사항 준수
- 개발자 편의성 향상

### 1.2 적용 서비스
- **전자결제(PG) 서비스**: 신용카드, 계좌이체, 가상계좌, 휴대폰결제 등
- **내통장결제 서비스**: 간편현금결제 기반 계좌 등록 후 결제
- **간편현금결제 서비스**: 실시간 펌뱅킹 기반 현금결제
- **화이트라벨 서비스**: 간편현금결제 및 신용카드 통합 서비스

## 2. 암호화 스펙 개요

### 2.1 기본 정보
- **⚠️ 주의**: 상세 스펙은 각 서비스별 섹션에서 확인하세요
- **AES 알고리즘**: 모든 서비스에서 AES-256/ECB/PKCS5Padding 사용
- **해시 알고리즘**: 모든 서비스에서 SHA-256 사용
- **중요**: 해시 생성 방식은 서비스별로 완전히 다름 (파라미터명, 필드 순서, 포함 항목이 모두 다름)

## 3. 테스트 환경 키 정보

### 3.1 테스트용 암호화키
| 서비스 | 테스트베드 키 | 키 길이 |
|--------|---------------|---------|
| **PG** | `pgSettle30y739r82jtd709yOfZ2yK5K` | 32byte |
| **내통장결제** | `SETTLEBANKISGOODSETTLEBANKISGOOD` | 32byte |
| **간편현금결제** | `pgSettle30y739r82jtd709yOfZ2yK5K` | 32byte |
| **화이트라벨** | `pgSettle30y739r82jtd709yOfZ2yK5K` | 32byte |

### 3.2 테스트용 해시키 (인증키)
| 서비스 | 테스트용 해시키 | 용도 |
|--------|----------------|------|
| **PG** | `ST1009281328226982205` | pktHash 생성용 |
| **내통장결제** | `SETTLEBANKISGOODSETTLEBANKISGOOD` | signature 생성용 |
| **간편현금결제** | `pgSettle30y739r82jtd709yOfZ2yK5K` | pktHash 생성용 |
| **화이트라벨** | `pgSettle30y739r82jtd709yOfZ2yK5K` | pktHash 생성용 |

## 4. 서비스별 암호화 정보

### 4.1 전자결제(PG) 서비스

#### 암호화 스펙
- **알고리즘**: AES-256/ECB/PKCS5Padding
- **인코딩**: Base64 Encoding
- **암호화 대상 필드**: 거래금액, 고객명, 휴대폰번호, 이메일, 카드번호, 유효기간, 식별번호, 카드비밀번호

#### 해시 생성 방법
- **해시 파라미터명**: `pktHash`
- **신용카드 결제 (UI)**
```
해시값 = SHA256(상점아이디 + 결제수단 + 상점주문번호 + 요청일자 + 요청시간 + 거래금액(평문) + 해쉬키)
```

##### 신용카드 빌키 결제 (Non-UI)
```
해시값 = SHA256(거래일자 + 거래시간 + 상점아이디 + 상점주문번호 + 거래금액(평문) + 해쉬키)
```

##### 신용카드 빌키 삭제
```
해시값 = SHA256(거래일자 + 거래시간 + 상점아이디 + 상점주문번호 + "0" + 해쉬키)
```

##### 가상계좌 채번
```
해시값 = SHA256(거래일자 + 거래시간 + 상점아이디 + 상점주문번호 + 거래금액(평문) + 해쉬키)
```

##### 휴대폰 결제
```
해시값 = SHA256(상점아이디 + 결제수단 + 상점주문번호 + 요청일자 + 요청시간 + 거래금액(평문) + 해쉬키)
```

##### 카카오페이 간편결제
```
해시값 = SHA256(상점아이디 + 결제수단 + 상점주문번호 + 요청일자 + 요청시간 + 거래금액(평문) + 해쉬키)
```

##### 포인트다모아 결제
```
해시값 = SHA256(상점아이디 + 결제수단 + 상점주문번호 + 요청일자 + 요청시간 + 거래금액(평문) + 해쉬키)
```

#### 노티 전문 해시 검증
```
해시값 = SHA256(거래상태코드 + 거래일자 + 거래시간 + 상점아이디 + 상점주문번호 + 거래금액 + 해쉬키)
```

#### PG 서비스 전용 암호화/해시 생성 샘플 코드

##### Java 예제
```java
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import java.util.Base64;

public class PGEncryption {
    
    // AES 암호화 (Base64 인코딩)
    public static String encryptAES(String plainText, String key) throws Exception {
        SecretKeySpec secretKey = new SecretKeySpec(key.getBytes("UTF-8"), "AES");
        Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE, secretKey);
        byte[] encryptedBytes = cipher.doFinal(plainText.getBytes("UTF-8"));
        return Base64.getEncoder().encodeToString(encryptedBytes);
    }
    
    // SHA-256 해시 생성
    public static String generateHash(String input) throws NoSuchAlgorithmException {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] hashBytes = md.digest(input.getBytes("UTF-8"));
        
        StringBuilder sb = new StringBuilder();
        for (byte b : hashBytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }
    
    // 신용카드 결제 해시 생성
    public static String generateCardHash(String mchtId, String method, String mchtTrdNo, 
                                        String trdDt, String trdTm, String trdAmt, String hashKey) throws NoSuchAlgorithmException {
        String input = mchtId + method + mchtTrdNo + trdDt + trdTm + trdAmt + hashKey;
        return generateHash(input);
    }
    
    // 가상계좌 채번 해시 생성
    public static String generateVBankHash(String trdDt, String trdTm, String mchtId, 
                                         String mchtTrdNo, String trdAmt, String hashKey) throws NoSuchAlgorithmException {
        String input = trdDt + trdTm + mchtId + mchtTrdNo + trdAmt + hashKey;
        return generateHash(input);
    }
    
    // 휴대폰 결제 해시 생성
    public static String generateMobileHash(String mchtId, String method, String mchtTrdNo, 
                                          String trdDt, String trdTm, String trdAmt, String hashKey) throws NoSuchAlgorithmException {
        String input = mchtId + method + mchtTrdNo + trdDt + trdTm + trdAmt + hashKey;
        return generateHash(input);
    }
    
    // 노티 전문 해시 검증
    public static String generateNotiHash(String trdStatCd, String trdDt, String trdTm, 
                                        String mchtId, String mchtTrdNo, String trdAmt, String hashKey) throws NoSuchAlgorithmException {
        String input = trdStatCd + trdDt + trdTm + mchtId + mchtTrdNo + trdAmt + hashKey;
        return generateHash(input);
    }
}

// 사용 예시
public class PGExample {
    public static void main(String[] args) throws Exception {
        // 테스트용 키
        String testEncryptKey = "pgSettle30y739r82jtd709yOfZ2yK5K";
        String testHashKey = "ST1009281328226982205";
        
        // 개인정보 암호화
        String encryptedAmount = PGEncryption.encryptAES("1000", testEncryptKey);
        String encryptedName = PGEncryption.encryptAES("홍길동", testEncryptKey);
        String encryptedPhone = PGEncryption.encryptAES("01012345678", testEncryptKey);
        
        // 신용카드 결제 해시 생성
        String cardHash = PGEncryption.generateCardHash("nxca_jt_il", "card", "ORDER20211231100000", 
                                                       "20211231", "100000", "1000", testHashKey);
        
        System.out.println("암호화된 금액: " + encryptedAmount);
        System.out.println("생성된 해시: " + cardHash);
    }
}
```

##### PHP 예제
```php
<?php
function encryptAES($plainText, $key) {
    $cipher = "aes-256-ecb";
    $options = OPENSSL_RAW_DATA;
    $encrypted = openssl_encrypt($plainText, $cipher, $key, $options);
    return base64_encode($encrypted);
}

function generateHash($input) {
    return hash('sha256', $input);
}

// 신용카드 결제 해시 생성
function generateCardHash($mchtId, $method, $mchtTrdNo, $trdDt, $trdTm, $trdAmt, $hashKey) {
    $input = $mchtId . $method . $mchtTrdNo . $trdDt . $trdTm . $trdAmt . $hashKey;
    return generateHash($input);
}

// 가상계좌 채번 해시 생성
function generateVBankHash($trdDt, $trdTm, $mchtId, $mchtTrdNo, $trdAmt, $hashKey) {
    $input = $trdDt . $trdTm . $mchtId . $mchtTrdNo . $trdAmt . $hashKey;
    return generateHash($input);
}

// 테스트용 키
$testEncryptKey = "pgSettle30y739r82jtd709yOfZ2yK5K";
$testHashKey = "ST1009281328226982205";

// 테스트
$hash = generateCardHash("nxca_jt_il", "card", "ORDER20211231100000", "20211231", "100000", "1000", $testHashKey);
echo "생성된 해시: " . $hash;
?>
```

##### JavaScript 예제
```javascript
// SHA-256 해시 생성 (CryptoJS 사용)
function generateHash(input) {
    return CryptoJS.SHA256(input).toString();
}

// 신용카드 결제 해시 생성
function generateCardHash(mchtId, method, mchtTrdNo, trdDt, trdTm, trdAmt, hashKey) {
    const input = mchtId + method + mchtTrdNo + trdDt + trdTm + trdAmt + hashKey;
    return generateHash(input);
}

// 가상계좌 채번 해시 생성
function generateVBankHash(trdDt, trdTm, mchtId, mchtTrdNo, trdAmt, hashKey) {
    const input = trdDt + trdTm + mchtId + mchtTrdNo + trdAmt + hashKey;
    return generateHash(input);
}

// 테스트용 키
const testHashKey = "ST1009281328226982205";

// 테스트
const hash = generateCardHash("nxca_jt_il", "card", "ORDER20211231100000", "20211231", "100000", "1000", testHashKey);
console.log("생성된 해시:", hash);
```

### 4.2 내통장결제 서비스

#### 암호화 스펙
- **알고리즘**: AES-256/ECB/PKCS5Padding
- **인코딩**: Hex Encoding
- **암호화 대상 필드**: 거래금액, 고객명, 휴대폰번호, 이메일, 계좌번호

#### 해시 생성 방법
- **해시 파라미터명**: `signature`
- **결제인증 (버전별)**
```
1.0: 해시값 = SHA256(상점아이디 + 주문번호 + 거래일자 + 거래시간 + 거래금액 + 인증키)
2.0: 해시값 = SHA256(상점아이디 + 주문번호 + 거래일자 + 거래시간 + 거래금액 + 결과통보URL_HOST + 인증키)
```

##### 결제취소
```
해시값 = SHA256(상점아이디 + 주문번호 + 취소요청일자 + 취소요청시간 + 취소금액 + 해쉬키)
```

#### 내통장결제 서비스 전용 암호화/해시 생성 샘플 코드

##### Java 예제
```java
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import java.util.HexFormat;

public class HectoFinancialEncryption {
    
    // AES 암호화 (Hex 인코딩)
    public static String encryptAES(String plainText, String key) throws Exception {
        SecretKeySpec secretKey = new SecretKeySpec(key.getBytes("UTF-8"), "AES");
        Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE, secretKey);
        byte[] encryptedBytes = cipher.doFinal(plainText.getBytes("UTF-8"));
        return HexFormat.of().formatHex(encryptedBytes);
    }
    
    // SHA-256 해시 생성
    public static String generateHash(String input) throws NoSuchAlgorithmException {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] hashBytes = md.digest(input.getBytes("UTF-8"));
        
        StringBuilder sb = new StringBuilder();
        for (byte b : hashBytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }
    
    // 결제인증 해시 생성
    public static String generateHectoFinancialHash(String mchtId, String ordNo, String trDay, 
                                                   String trTime, String trdAmt, String hashKey) throws NoSuchAlgorithmException {
        String input = mchtId + ordNo + trDay + trTime + trdAmt + hashKey;
        return generateHash(input);
    }
    
    // 결제취소 해시 생성
    public static String generateCancelHash(String mchtId, String ordNo, String cancelReqDt, 
                                          String cancelReqTm, String cancelAmt, String hashKey) throws NoSuchAlgorithmException {
        String input = mchtId + ordNo + cancelReqDt + cancelReqTm + cancelAmt + hashKey;
        return generateHash(input);
    }
}

// 사용 예시
public class HectoFinancialExample {
    public static void main(String[] args) throws Exception {
        // 테스트용 키
        String testEncryptKey = "SETTLEBANKISGOODSETTLEBANKISGOOD";
        String testHashKey = "SETTLEBANKISGOODSETTLEBANKISGOOD";
        
        // 개인정보 암호화
        String encryptedAmount = HectoFinancialEncryption.encryptAES("1000", testEncryptKey);
        String encryptedName = HectoFinancialEncryption.encryptAES("홍길동", testEncryptKey);
        String encryptedPhone = HectoFinancialEncryption.encryptAES("01012345678", testEncryptKey);
        
        // 결제인증 해시 생성
        String settleHash = HectoFinancialEncryption.generateHectoFinancialHash("nxca_jt_il", "ORDER20211231100000", 
                                                                               "20211231", "100000", "1000", testHashKey);
        
        System.out.println("암호화된 금액: " + encryptedAmount);
        System.out.println("생성된 해시: " + settleHash);
    }
}
```

##### PHP 예제
```php
<?php
function encryptAES($plainText, $key) {
    $cipher = "aes-256-ecb";
    $options = OPENSSL_RAW_DATA;
    $encrypted = openssl_encrypt($plainText, $cipher, $key, $options);
    return bin2hex($encrypted);
}

function generateHash($input) {
    return hash('sha256', $input);
}

// 결제인증 해시 생성
function generateHectoFinancialHash($mchtId, $ordNo, $trDay, $trTime, $trdAmt, $hashKey) {
    $input = $mchtId . $ordNo . $trDay . $trTime . $trdAmt . $hashKey;
    return generateHash($input);
}

// 결제취소 해시 생성
function generateCancelHash($mchtId, $ordNo, $cancelReqDt, $cancelReqTm, $cancelAmt, $hashKey) {
    $input = $mchtId . $ordNo . $cancelReqDt . $cancelReqTm . $cancelAmt . $hashKey;
    return generateHash($input);
}

// 테스트용 키
$testEncryptKey = "SETTLEBANKISGOODSETTLEBANKISGOOD";
$testHashKey = "SETTLEBANKISGOODSETTLEBANKISGOOD";

// 테스트
$hash = generateHectoFinancialHash("nxca_jt_il", "ORDER20211231100000", "20211231", "100000", "1000", $testHashKey);
echo "생성된 해시: " . $hash;
?>
```

##### JavaScript 예제
```javascript
// SHA-256 해시 생성 (CryptoJS 사용)
function generateHash(input) {
    return CryptoJS.SHA256(input).toString();
}

// 결제인증 해시 생성
function generateHectoFinancialHash(mchtId, ordNo, trDay, trTime, trdAmt, hashKey) {
    const input = mchtId + ordNo + trDay + trTime + trdAmt + hashKey;
    return generateHash(input);
}

// 결제취소 해시 생성
function generateCancelHash(mchtId, ordNo, cancelReqDt, cancelReqTm, cancelAmt, hashKey) {
    const input = mchtId + ordNo + cancelReqDt + cancelReqTm + cancelAmt + hashKey;
    return generateHash(input);
}

// 테스트용 키
const testHashKey = "SETTLEBANKISGOODSETTLEBANKISGOOD";

// 테스트
const hash = generateHectoFinancialHash("nxca_jt_il", "ORDER20211231100000", "20211231", "100000", "1000", testHashKey);
console.log("생성된 해시:", hash);
```

### 4.3 간편현금결제 서비스

#### 암호화 스펙
- **알고리즘**: AES-256/ECB/PKCS5Padding
- **인코딩**: Base64 Encoding
- **암호화 대상 필드**: 거래금액, 고객명, 휴대폰번호, 이메일

#### 해시 생성 방법
- **해시 파라미터명**: `pktHash`
- **휴대폰 본인인증 요청**
```
해시값 = SHA256(상점아이디 + 고객아이디(평문) + 요청일자 + 요청시간 + 생년월일(평문) + 휴대폰번호(평문) + 인증구분 + 인증키)
```

##### 결제취소
```
해시값 = SHA256(상점아이디 + 주문번호 + 취소요청일자 + 취소요청시간 + 취소금액 + 해쉬키)
```

#### 간편현금결제 서비스 전용 암호화/해시 생성 샘플 코드

##### Java 예제
```java
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import java.util.Base64;

public class EzCPEncryption {
    
    // AES 암호화 (Base64 인코딩)
    public static String encryptAES(String plainText, String key) throws Exception {
        SecretKeySpec secretKey = new SecretKeySpec(key.getBytes("UTF-8"), "AES");
        Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE, secretKey);
        byte[] encryptedBytes = cipher.doFinal(plainText.getBytes("UTF-8"));
        return Base64.getEncoder().encodeToString(encryptedBytes);
    }
    
    // SHA-256 해시 생성
    public static String generateHash(String input) throws NoSuchAlgorithmException {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] hashBytes = md.digest(input.getBytes("UTF-8"));
        
        StringBuilder sb = new StringBuilder();
        for (byte b : hashBytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }
    
    // 결제창 호출 해시 생성
    public static String generatePaymentHash(String mchtId, String method, String mchtTrdNo, 
                                           String trdDt, String trdTm, String trdAmt, String hashKey) throws NoSuchAlgorithmException {
        String input = mchtId + method + mchtTrdNo + trdDt + trdTm + trdAmt + hashKey;
        return generateHash(input);
    }
    
    // 결제취소 해시 생성
    public static String generateCancelHash(String mchtId, String ordNo, String cancelReqDt, 
                                          String cancelReqTm, String cancelAmt, String hashKey) throws NoSuchAlgorithmException {
        String input = mchtId + ordNo + cancelReqDt + cancelReqTm + cancelAmt + hashKey;
        return generateHash(input);
    }
}

// 사용 예시
public class EzCPExample {
    public static void main(String[] args) throws Exception {
        // 테스트용 키
        String testEncryptKey = "pgSettle30y739r82jtd709yOfZ2yK5K";
        String testHashKey = "pgSettle30y739r82jtd709yOfZ2yK5K";
        
        // 개인정보 암호화
        String encryptedAmount = EzCPEncryption.encryptAES("1000", testEncryptKey);
        String encryptedName = EzCPEncryption.encryptAES("홍길동", testEncryptKey);
        String encryptedPhone = EzCPEncryption.encryptAES("01012345678", testEncryptKey);
        
        // 결제창 호출 해시 생성
        String paymentHash = EzCPEncryption.generatePaymentHash("nxca_jt_il", "ezcp", "ORDER20211231100000", 
                                                               "20211231", "100000", "1000", testHashKey);
        
        System.out.println("암호화된 금액: " + encryptedAmount);
        System.out.println("생성된 해시: " + paymentHash);
    }
}
```

##### PHP 예제
```php
<?php
function encryptAES($plainText, $key) {
    $cipher = "aes-256-ecb";
    $options = OPENSSL_RAW_DATA;
    $encrypted = openssl_encrypt($plainText, $cipher, $key, $options);
    return base64_encode($encrypted);
}

function generateHash($input) {
    return hash('sha256', $input);
}

// 결제창 호출 해시 생성
function generatePaymentHash($mchtId, $method, $mchtTrdNo, $trdDt, $trdTm, $trdAmt, $hashKey) {
    $input = $mchtId . $method . $mchtTrdNo . $trdDt . $trdTm . $trdAmt . $hashKey;
    return generateHash($input);
}

// 결제취소 해시 생성
function generateCancelHash($mchtId, $ordNo, $cancelReqDt, $cancelReqTm, $cancelAmt, $hashKey) {
    $input = $mchtId . $ordNo . $cancelReqDt . $cancelReqTm . $cancelAmt . $hashKey;
    return generateHash($input);
}

// 테스트용 키
$testEncryptKey = "pgSettle30y739r82jtd709yOfZ2yK5K";
$testHashKey = "pgSettle30y739r82jtd709yOfZ2yK5K";

// 테스트
$hash = generatePaymentHash("nxca_jt_il", "ezcp", "ORDER20211231100000", "20211231", "100000", "1000", $testHashKey);
echo "생성된 해시: " . $hash;
?>
```

##### JavaScript 예제
```javascript
// SHA-256 해시 생성 (CryptoJS 사용)
function generateHash(input) {
    return CryptoJS.SHA256(input).toString();
}

// 결제창 호출 해시 생성
function generatePaymentHash(mchtId, method, mchtTrdNo, trdDt, trdTm, trdAmt, hashKey) {
    const input = mchtId + method + mchtTrdNo + trdDt + trdTm + trdAmt + hashKey;
    return generateHash(input);
}

// 결제취소 해시 생성
function generateCancelHash(mchtId, ordNo, cancelReqDt, cancelReqTm, cancelAmt, hashKey) {
    const input = mchtId + ordNo + cancelReqDt + cancelReqTm + cancelAmt + hashKey;
    return generateHash(input);
}

// 테스트용 키
const testHashKey = "pgSettle30y739r82jtd709yOfZ2yK5K";

// 테스트
const hash = generatePaymentHash("nxca_jt_il", "ezcp", "ORDER20211231100000", "20211231", "100000", "1000", testHashKey);
console.log("생성된 해시:", hash);
```

### 4.4 화이트라벨 서비스

#### 암호화 스펙
- **알고리즘**: AES-256/ECB/PKCS5Padding
- **인코딩**: Base64 Encoding
- **암호화 대상 필드**: 거래금액, 고객ID, 이메일, 휴대폰번호

#### 해시 생성 방법
- **해시 파라미터명**: `pktHash`
- **결제창 호출**
```
해시값 = SHA256(상점아이디 + 결제수단 + 상점주문번호 + 요청일자 + 요청시간 + 거래금액 + 해쉬키)
```

##### 결제취소
```
해시값 = SHA256(취소요청일자 + 취소요청시간 + 상점아이디 + 상점주문번호 + 취소금액 + 해쉬키)
```

##### 실시간 거래 조회
```
해시값 = SHA256(상점아이디 + 결제수단 + 상점주문번호 + 요청일자 + 요청시간 + 거래금액 + 해쉬키)
```

#### 화이트라벨 서비스 전용 암호화/해시 생성 샘플 코드

##### Java 예제
```java
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import java.util.Base64;

public class WhiteLabelEncryption {
    
    // AES 암호화 (Base64 인코딩)
    public static String encryptAES(String plainText, String key) throws Exception {
        SecretKeySpec secretKey = new SecretKeySpec(key.getBytes("UTF-8"), "AES");
        Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE, secretKey);
        byte[] encryptedBytes = cipher.doFinal(plainText.getBytes("UTF-8"));
        return Base64.getEncoder().encodeToString(encryptedBytes);
    }
    
    // SHA-256 해시 생성
    public static String generateHash(String input) throws NoSuchAlgorithmException {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] hashBytes = md.digest(input.getBytes("UTF-8"));
        
        StringBuilder sb = new StringBuilder();
        for (byte b : hashBytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }
    
    // 결제창 호출 해시 생성
    public static String generatePaymentHash(String mchtId, String method, String mchtTrdNo, 
                                           String trdDt, String trdTm, String trdAmt, String hashKey) throws NoSuchAlgorithmException {
        String input = mchtId + method + mchtTrdNo + trdDt + trdTm + trdAmt + hashKey;
        return generateHash(input);
    }
    
    // 결제 취소 해시 생성
    public static String generateCancelHash(String cancelReqDt, String cancelReqTm, String mchtId, 
                                          String mchtTrdNo, String cancelAmt, String hashKey) throws NoSuchAlgorithmException {
        String input = cancelReqDt + cancelReqTm + mchtId + mchtTrdNo + cancelAmt + hashKey;
        return generateHash(input);
    }
    
    // 실시간 거래 조회 해시 생성
    public static String generateInquiryHash(String mchtId, String method, String mchtTrdNo, 
                                           String trdDt, String trdTm, String trdAmt, String hashKey) throws NoSuchAlgorithmException {
        String input = mchtId + method + mchtTrdNo + trdDt + trdTm + trdAmt + hashKey;
        return generateHash(input);
    }
}

// 사용 예시
public class WhiteLabelExample {
    public static void main(String[] args) throws Exception {
        // 테스트용 키
        String testEncryptKey = "pgSettle30y739r82jtd709yOfZ2yK5K";
        String testHashKey = "pgSettle30y739r82jtd709yOfZ2yK5K";
        
        // 개인정보 암호화
        String encryptedAmount = WhiteLabelEncryption.encryptAES("500", testEncryptKey);
        String encryptedCustId = WhiteLabelEncryption.encryptAES("HongGilDong", testEncryptKey);
        String encryptedEmail = WhiteLabelEncryption.encryptAES("test@example.com", testEncryptKey);
        
        // 결제창 호출 해시 생성
        String paymentHash = WhiteLabelEncryption.generatePaymentHash("pg_test", "WL", "WL_Info_20210806075154649", 
                                                                    "20210806", "080101", "500", testHashKey);
        
        System.out.println("암호화된 금액: " + encryptedAmount);
        System.out.println("생성된 해시: " + paymentHash);
    }
}
```

##### PHP 예제
```php
<?php
function encryptAES($plainText, $key) {
    $cipher = "aes-256-ecb";
    $options = OPENSSL_RAW_DATA;
    $encrypted = openssl_encrypt($plainText, $cipher, $key, $options);
    return base64_encode($encrypted);
}

function generateHash($input) {
    return hash('sha256', $input);
}

// 결제창 호출 해시 생성
function generatePaymentHash($mchtId, $method, $mchtTrdNo, $trdDt, $trdTm, $trdAmt, $hashKey) {
    $input = $mchtId . $method . $mchtTrdNo . $trdDt . $trdTm . $trdAmt . $hashKey;
    return generateHash($input);
}

// 결제 취소 해시 생성
function generateCancelHash($cancelReqDt, $cancelReqTm, $mchtId, $mchtTrdNo, $cancelAmt, $hashKey) {
    $input = $cancelReqDt . $cancelReqTm . $mchtId . $mchtTrdNo . $cancelAmt . $hashKey;
    return generateHash($input);
}

// 실시간 거래 조회 해시 생성
function generateInquiryHash($mchtId, $method, $mchtTrdNo, $trdDt, $trdTm, $trdAmt, $hashKey) {
    $input = $mchtId . $method . $mchtTrdNo . $trdDt . $trdTm . $trdAmt . $hashKey;
    return generateHash($input);
}

// 테스트용 키
$testEncryptKey = "pgSettle30y739r82jtd709yOfZ2yK5K";
$testHashKey = "pgSettle30y739r82jtd709yOfZ2yK5K";

// 테스트
$hash = generatePaymentHash("pg_test", "WL", "WL_Info_20210806075154649", "20210806", "080101", "500", $testHashKey);
echo "생성된 해시: " . $hash;
?>
```

##### JavaScript 예제
```javascript
// SHA-256 해시 생성 (CryptoJS 사용)
function generateHash(input) {
    return CryptoJS.SHA256(input).toString();
}

// 결제창 호출 해시 생성
function generatePaymentHash(mchtId, method, mchtTrdNo, trdDt, trdTm, trdAmt, hashKey) {
    const input = mchtId + method + mchtTrdNo + trdDt + trdTm + trdAmt + hashKey;
    return generateHash(input);
}

// 결제 취소 해시 생성
function generateCancelHash(cancelReqDt, cancelReqTm, mchtId, mchtTrdNo, cancelAmt, hashKey) {
    const input = cancelReqDt + cancelReqTm + mchtId + mchtTrdNo + cancelAmt + hashKey;
    return generateHash(input);
}

// 실시간 거래 조회 해시 생성
function generateInquiryHash(mchtId, method, mchtTrdNo, trdDt, trdTm, trdAmt, hashKey) {
    const input = mchtId + method + mchtTrdNo + trdDt + trdTm + trdAmt + hashKey;
    return generateHash(input);
}

// 테스트용 키
const testHashKey = "pgSettle30y739r82jtd709yOfZ2yK5K";

// 테스트
const hash = generatePaymentHash("pg_test", "WL", "WL_Info_20210806075154649", "20210806", "080101", "500", testHashKey);
console.log("생성된 해시:", hash);
```

## 5. 공통 샘플 코드

### 5.1 Java 공통 유틸리티
```java
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import java.util.Base64;
import java.util.HexFormat;

public class EncryptionUtils {
    
    // AES 암호화 (Base64 인코딩)
    public static String encryptAESBase64(String plainText, String key) throws Exception {
        SecretKeySpec secretKey = new SecretKeySpec(key.getBytes("UTF-8"), "AES");
        Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE, secretKey);
        byte[] encryptedBytes = cipher.doFinal(plainText.getBytes("UTF-8"));
        return Base64.getEncoder().encodeToString(encryptedBytes);
    }
    
    // AES 암호화 (Hex 인코딩)
    public static String encryptAESHex(String plainText, String key) throws Exception {
        SecretKeySpec secretKey = new SecretKeySpec(key.getBytes("UTF-8"), "AES");
        Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE, secretKey);
        byte[] encryptedBytes = cipher.doFinal(plainText.getBytes("UTF-8"));
        return HexFormat.of().formatHex(encryptedBytes);
    }
    
    // SHA-256 해시 생성
    public static String generateHash(String input) throws NoSuchAlgorithmException {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] hashBytes = md.digest(input.getBytes("UTF-8"));
        
        StringBuilder sb = new StringBuilder();
        for (byte b : hashBytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }
}
```

### 5.2 PHP 공통 유틸리티
```php
<?php
// AES 암호화 (Base64 인코딩)
function encryptAESBase64($plainText, $key) {
    $cipher = "aes-256-ecb";
    $options = OPENSSL_RAW_DATA;
    $encrypted = openssl_encrypt($plainText, $cipher, $key, $options);
    return base64_encode($encrypted);
}

// AES 암호화 (Hex 인코딩)
function encryptAESHex($plainText, $key) {
    $cipher = "aes-256-ecb";
    $options = OPENSSL_RAW_DATA;
    $encrypted = openssl_encrypt($plainText, $cipher, $key, $options);
    return bin2hex($encrypted);
}

// SHA-256 해시 생성
function generateHash($input) {
    return hash('sha256', $input);
}
?>
```

### 5.3 JavaScript 공통 유틸리티
```javascript
// SHA-256 해시 생성 (CryptoJS 사용)
function generateHash(input) {
    return CryptoJS.SHA256(input).toString();
}

// AES 암호화 (CryptoJS 사용, Base64 인코딩)
function encryptAESBase64(plainText, key) {
    const encrypted = CryptoJS.AES.encrypt(plainText, key);
    return encrypted.toString();
}

// AES 암호화 (CryptoJS 사용, Hex 인코딩)
function encryptAESHex(plainText, key) {
    const encrypted = CryptoJS.AES.encrypt(plainText, key);
    return encrypted.ciphertext.toString();
}
```

## 6. 테스트 환경 설정

### 6.1 테스트용 키 사용법
- **암호화키**: AES 암호화에 사용
- **해시키**: SHA-256 해시 생성에 사용
- 개발/테스트 단계에서만 사용
- 운영 환경에서는 반드시 고유 키 사용

### 6.2 테스트 시나리오
1. 테스트용 암호화키로 개인정보 암호화
2. 테스트용 해시키로 해시값 생성
3. API 요청 전송 및 응답 확인
4. 해시 검증 성공 여부 확인

## 7. 운영 환경 전환

### 7.1 키 발급 절차
- 서비스 이행 시 별도 통보
- 가맹점별 고유 키 발급
- 암호화키와 해시키 모두 발급

### 7.2 보안 체크리스트
- [ ] 테스트베드 암호화키 제거 확인
- [ ] 테스트용 해시키 제거 확인
- [ ] 운영용 암호화키 적용 확인
- [ ] 운영용 해시키 적용 확인
- [ ] 로그 보안 설정 확인
- [ ] HTTPS 프로토콜 사용 확인

## 8. 인코딩 방식 가이드

### 8.1 서비스별 암호화 스펙 비교
| 서비스 | AES 알고리즘 | 암호화 인코딩 | 해시 파라미터명 | 해시 인코딩 | 비고 |
|--------|---------------|---------------|----------------|-------------|------|
| **PG** | AES-256/ECB/PKCS5Padding | Base64 | `pktHash` | Hex | 개인정보 암호화에 Base64 사용 |
| **내통장결제** | AES-256/ECB/PKCS5Padding | Hex | `signature` | Hex | 모든 데이터에 Hex 인코딩 사용 |
| **간편현금결제** | AES-256/ECB/PKCS5Padding | Base64 | `pktHash` | Hex | 개인정보 암호화에 Base64 사용 |
| **화이트라벨** | AES-256/ECB/PKCS5Padding | Base64 | `pktHash` | Hex | 개인정보 암호화에 Base64 사용 |

### 8.2 인코딩 방식 선택 기준
- **Base64**: 가독성이 좋고 URL 안전, 텍스트 기반 시스템에 적합
- **Hex**: 바이너리 데이터 처리에 효율적, 디버깅 시 용이

### 8.3 인코딩 변환 예시
```java
// Base64 → Hex 변환
String base64Data = "SGVsbG8gV29ybGQ=";
byte[] decodedBytes = Base64.getDecoder().decode(base64Data);
String hexData = HexFormat.of().formatHex(decodedBytes);

// Hex → Base64 변환
String hexData = "48656c6c6f20576f726c64";
byte[] bytes = HexFormat.of().parseHex(hexData);
String base64Data = Base64.getEncoder().encodeToString(bytes);
```

## 9. 보안 가이드라인

### 9.1 키 관리
- 테스트용 키는 절대 운영 환경에서 사용 금지
- 운영용 키는 안전한 방법으로 보관
- 정기적인 키 교체 권장

### 9.2 데이터 보안
- 개인정보는 반드시 암호화하여 전송
- 민감한 정보는 로그에 기록 금지
- HTTPS 프로토콜 사용 권장

### 9.3 접근 제어
- API 접근 IP 제한 설정
- 적절한 인증 및 권한 관리
- 정기적인 보안 감사 수행

---

**※ 본 문서는 헥토파이낸셜의 공식 연동 문서를 참고하여 작성되었습니다.**
**※ 최신 정보는 https://develop.sbsvc.online 에서 확인하시기 바랍니다.**
