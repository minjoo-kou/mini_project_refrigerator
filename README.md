# mini_project_refrigerator
항해99 5기 a반 11조 미니프로젝트

## 나만의 냉장고
나만의 냉장고를 만들어 장을 본 재료들의 정보와 유통기한 등을 적어서 등록해두고 관리하는 사이트 입니다.
![loginlogo](https://user-images.githubusercontent.com/78454645/149273940-6a8e2b7c-ffe0-489a-81d1-a9c97461030b.png)

## 웹사이트 링크
http://snowlove.shop/

## 시연영상
https://www.youtube.com/watch?v=58P7QdyZ3Mc

## 소개

* 프레임워크, 라이브러리를 다양하게 사용해보고 alert 과 modal을 사용해서 프로젝트 진행하였습니다.
* 여러가지 다양한 기능을 구현해보았습니다.

- login page
  <br>접속시 첫 화면이며, 회원가입 후 로그인을 하는 페이지입니다.</br>

- Main page
  <br>로그인 후 화면이며, 유저마다 자신이 등록한 재료를 볼 수 있습니다.
  <br>유저가 재료를 등록할 때 모달창
  <br>등록한 재료를 수정 및 삭제 가능

- Sign-in Page
  <br>입력한 값과 회원가입한 ID와 PW가 맞지 않을 시 error alert
  <br>로그인 시에 메인페이지로 이동

- Sign-up Page
  <br>정규표현식 적용 / 아이디 중복, 패스워드 일치 불일치 여부 확인 기능
  
  

## 기술 스택
- 개발 언어 : HTML5, CSS, javascript, python, Bootstrap
- 개발 환경 : flask web framework
- 데이터베이스 : mongodb
- 형상관리 툴 : git
- Server : AWS EC2 (Ubuntu 18.04 LTS) 


## 요구 사항
### SSR vs CSR
- SSR은 한 번에 그려지는 장점, SEO에 강점
- CSR은 전체적인 시간은 SSR보다 비슷하거나 더 오래 걸릴 수도 있지만 로딩창을 먼저 보여줌으로써 사용자의 인내심을 늘려준다.

### JWT
- 발급 후 토큰 검증만 하면 되기 때문에 추가 저장소가 필요 없다. 가볍다.
- 필요한 모든 정보를 자체적으로 지니고 있기(self-contained)때문에 두 개체 사이에서 손쉽게 전달 될 수 있다.
