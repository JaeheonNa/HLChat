from typing import override
import httpx

from fastapi import Depends, HTTPException

from adapter.output.userPersistenceAdapter import RequestUserPersistenceAdapter
from application.port.output.userPort import MariaUserPort
from config import kakao_client_id, kakao_client_secret, kakao_redirect_uri
from domain.response import KakaoAuthUrlResponse, KakaoCallbackResponse, JWTResponse
from domain.userDomain import UserDomain
from domain.userRequest import KakaoRegisterRequest


KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"


class KakaoAuthService:
    def __init__(self,
                 mariaUserPort: MariaUserPort = Depends(RequestUserPersistenceAdapter)):
        self.mariaUserPort = mariaUserPort

    async def getKakaoAuthUrl(self) -> KakaoAuthUrlResponse:
        auth_url = (
            f"{KAKAO_AUTH_URL}"
            f"?client_id={kakao_client_id}"
            f"&redirect_uri={kakao_redirect_uri}"
            f"&response_type=code"
        )
        return KakaoAuthUrlResponse(auth_url=auth_url)

    async def handleKakaoCallback(self, code: str, auto_register: bool = True) -> KakaoCallbackResponse:
        access_token = await self._getKakaoAccessToken(code)
        kakao_user_info = await self._getKakaoUserInfo(access_token)

        provider_id = str(kakao_user_info.get("id"))
        kakao_account = kakao_user_info.get("kakao_account", {})
        profile = kakao_account.get("profile", {})

        # 비즈니스 앱: 실명, 전화번호 사용 / 일반 앱: 닉네임 사용
        name = kakao_account.get("name") or profile.get("nickname") or "카카오사용자"
        email = kakao_account.get("email")
        profile_image = profile.get("profile_image_url")

        # 전화번호: +82 10-1234-5678 → 01012345678 변환
        phone_number = kakao_account.get("phone_number")
        if phone_number:
            phone_number = phone_number.replace("+82 ", "0").replace("-", "")

        existing_user = await self.mariaUserPort.findUserByProviderId("KAKAO", provider_id)

        if existing_user:
            jwt_token = existing_user.createJWT()
            return KakaoCallbackResponse(
                requires_registration=False,
                access_token=jwt_token,
                user_id=existing_user.userId,
                username=existing_user.username
            )
        elif auto_register:
            # 이름+전화번호로 기존 계정 확인 → 자동 연동
            if name and phone_number:
                print(f"[Kakao] 기존 계정 확인 - name: '{name}', phone: '{phone_number}'")
                existing_local_user = await self.mariaUserPort.findUserByNameAndPhone(name, phone_number)
                print(f"[Kakao] 조회 결과: {existing_local_user}")
                if existing_local_user:
                    print(f"[Kakao] 기존 계정 provider: '{existing_local_user.provider}'")
                if existing_local_user and existing_local_user.provider.upper() == 'LOCAL':
                    # 기존 계정에 카카오 연동
                    existing_local_user.provider = "KAKAO"
                    existing_local_user.provider_id = provider_id
                    if profile_image:
                        existing_local_user.profile_image = profile_image
                    await self.mariaUserPort.saveUser(existing_local_user)

                    jwt_token = existing_local_user.createJWT()
                    return KakaoCallbackResponse(
                        requires_registration=False,
                        access_token=jwt_token,
                        user_id=existing_local_user.userId,
                        username=existing_local_user.username
                    )

            # 기존 계정 없으면 신규 가입
            user_id = f"KAKAO_{provider_id}"
            request = KakaoRegisterRequest(
                provider="KAKAO",
                provider_id=provider_id,
                user_id=user_id,
                user_name=name,
                email=email,
                phone=phone_number,
                profile_image=profile_image
            )
            user_domain = UserDomain.createKakaoUser(request)
            await self.mariaUserPort.saveUser(user_domain)

            jwt_token = user_domain.createJWT()
            return KakaoCallbackResponse(
                requires_registration=False,
                access_token=jwt_token,
                user_id=user_id,
                username=name
            )
        else:
            # 연동 모드: provider_id만 반환
            return KakaoCallbackResponse(
                requires_registration=True,
                provider_id=provider_id,
                nickname=name,
                email=email,
                phone=phone_number,
                profile_image=profile_image
            )

    async def checkExistingUser(self, user_name: str, phone: str) -> KakaoCallbackResponse | None:
        if not user_name or not phone:
            return None

        existing_user = await self.mariaUserPort.findUserByNameAndPhone(user_name, phone)
        if existing_user and existing_user.provider == 'LOCAL':
            return KakaoCallbackResponse(
                requires_registration=True,
                existing_user_id=existing_user.userId,
                existing_user_name=existing_user.username
            )
        return None

    async def registerKakaoUser(self, request: KakaoRegisterRequest) -> JWTResponse:
        existing_user_by_id = await self.mariaUserPort.findUserByUserId(request.user_id)
        if existing_user_by_id:
            raise HTTPException(status_code=400, detail="이미 존재하는 사번입니다")

        existing_user_by_provider = await self.mariaUserPort.findUserByProviderId(
            request.provider, request.provider_id
        )
        if existing_user_by_provider:
            raise HTTPException(status_code=400, detail="이미 카카오 계정이 연동된 사용자가 있습니다")

        user_domain = UserDomain.createKakaoUser(request)
        await self.mariaUserPort.saveUser(user_domain)

        jwt_token = user_domain.createJWT()
        return JWTResponse(
            access_token=jwt_token,
            username=user_domain.username,
            password_expired=False
        )

    async def linkKakaoAccount(self, user_id: str, provider: str, provider_id: str) -> JWTResponse:
        existing_user_by_provider = await self.mariaUserPort.findUserByProviderId(provider, provider_id)
        if existing_user_by_provider:
            raise HTTPException(status_code=400, detail="이미 카카오 계정이 연동된 사용자가 있습니다")

        user_domain = await self.mariaUserPort.findUserByUserId(user_id)
        if user_domain is None:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

        if user_domain.provider != 'LOCAL':
            raise HTTPException(status_code=400, detail="이미 다른 계정이 연동되어 있습니다")

        user_domain.provider = provider
        user_domain.provider_id = provider_id
        await self.mariaUserPort.saveUser(user_domain)

        jwt_token = user_domain.createJWT()
        return JWTResponse(
            access_token=jwt_token,
            username=user_domain.username,
            password_expired=False
        )

    async def _getKakaoAccessToken(self, code: str) -> str:
        async with httpx.AsyncClient() as client:
            request_data = {
                "grant_type": "authorization_code",
                "client_id": kakao_client_id,
                "redirect_uri": kakao_redirect_uri,
                "code": code
            }
            if kakao_client_secret:
                request_data["client_secret"] = kakao_client_secret
            print(f"[Kakao Token Request] redirect_uri: {kakao_redirect_uri}")

            response = await client.post(
                KAKAO_TOKEN_URL,
                data=request_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            if response.status_code != 200:
                error_detail = response.json()
                print(f"[Kakao Token Error] {response.status_code}: {error_detail}")
                raise HTTPException(
                    status_code=400,
                    detail=f"카카오 토큰 발급에 실패했습니다: {error_detail.get('error_description', error_detail.get('error', 'Unknown error'))}"
                )

            token_data = response.json()
            return token_data.get("access_token")

    async def _getKakaoUserInfo(self, access_token: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                KAKAO_USER_INFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )

            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="카카오 사용자 정보 조회에 실패했습니다")

            return response.json()
