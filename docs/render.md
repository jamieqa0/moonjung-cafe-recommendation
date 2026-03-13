Render(렌더)에 서비스를 배포할 때, [.env](cci:7://file:///e:/study/moonbbang-station/.env:0:0-0:0) 파일에 있는 API 키 같은 민감한 정보들은 **보안을 위해 코드 저장소(GitHub)에 올리지 않고 Render 대시보드에서 직접 입력**해야 합니다.

설정하는 방법은 매우 간단합니다. 다음 두 가지 방법 중 하나를 선택하시면 됩니다.

### 방법 1. Environment Variables 탭에서 입력하기 (가장 일반적인 방법)

1. Render 대시보드에 로그인하고 배포한 **Web Service**를 클릭합니다.
2. 왼쪽 메뉴에서 **Environment** 탭을 클릭합니다.
3. **Add Environment Variable** 버튼을 클릭합니다.
4. 로컬의 [.env](cci:7://file:///e:/study/moonbbang-station/.env:0:0-0:0) 파일에 있는 내용을 하나씩 복사해서 넣습니다.
   * `Key`: [.env](cci:7://file:///e:/study/moonbbang-station/.env:0:0-0:0)의 왼쪽 부분 (예: `KAKAO_API_KEY`)
   * `Value`: [.env](cci:7://file:///e:/study/moonbbang-station/.env:0:0-0:0)의 오른쪽 부분 (예: `본인의_카카오_키_값`)
5. **Save Changes**를 눌러 저장합니다. (저장 후 서비스가 자동으로 다시 시작되며 환경 변수가 적용됩니다.)

<br>

### 방법 2. [.env](cci:7://file:///e:/study/moonbbang-station/.env:0:0-0:0) 파일 내용 통째로 복사해서 붙여넣기 (키가 많을 때 추천)

1. **Environment** 탭에서 **Environment Variables** 항목 옆의 **Add from .env** 버튼을 클릭합니다.
2. 로컬 컴퓨터에 있는 [.env](cci:7://file:///e:/study/moonbbang-station/.env:0:0-0:0) 파일의 내용 전체를 복사해서 나타나는 입력창에 그대로 붙여넣습니다. (단, `FLASK_ENV=development` 같은 로컬 전용 설정은 빼고 넣는 것이 좋습니다.)
3. **Save Changes**를 눌러 저장합니다.

<br>

### ⚠️ 주의사항
* [.env](cci:7://file:///e:/study/moonbbang-station/.env:0:0-0:0) 파일 자체가 GitHub에 올라가지 않도록, 프로젝트 루트 폴더에 있는 [.gitignore](cci:7://file:///e:/study/moonbbang-station/.gitignore:0:0-0:0) 파일 안에 [.env](cci:7://file:///e:/study/moonbbang-station/.env:0:0-0:0)가 잘 적혀 있는지 꼭 확인하세요! (이미 그렇게 설정되어 있으니 안심하셔도 됩니다.)
* [render.yaml](cci:7://file:///e:/study/moonbbang-station/render.yaml:0:0-0:0) 파일을 사용해서 인프라스트럭처를 코드로 관리(IaC)하고 계시다면, 해당 파일 안에 `envVars`를 정의하고 `sync: false` 설정을 통해 대시보드에서 안전하게 값을 넣도록 구성할 수도 있습니다. 하지만 지금은 위의 '방법 1'이나 '방법 2'가 가장 직관적이고 표준적인 방법입니다.

<br>

### 🗺️ 카카오 지도 API 사용 시 (401 Unauthorized 에러 해결)

Render에 배포한 후 지도가 나타나지 않는다면 카카오 개발자 센터에서 **허용된 도메인**에 Render 주소를 추가해야 합니다.

1. [카카오 디벨로퍼스(Kakao Developers)](https://developers.kakao.com/)에 접속하여 로그인합니다.
2. 내 애플리케이션 -> **내 애플리케이션 이름**을 클릭합니다.
3. 왼쪽 메뉴에서 **'플랫폼'**을 클릭합니다.
4. **'Web'** 플랫폼 카테고리의 **[수정]** 버튼을 누릅니다.
5. "사이트 도메인" 입력칸에 **현재 배포된 Render 웹사이트의 전체 주소**를 추가합니다. (줄 바꿈으로 여러 개 등록 가능)
   * 예: `https://moonbbang-station.onrender.com` (마지막 끝에 슬래시 `/` 는 빼고 적습니다)
   * 기존에 작성된 `http://localhost:8000` 등은 로컬 개발을 위해 지우지 말고 그대로 두세요.
6. **[저장]** 버튼을 누르고, 배포된 사이트에서 약 5분 후 새로고침 해보세요.
7. JS 도 똑같이 저장해야함