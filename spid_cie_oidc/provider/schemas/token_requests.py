from typing import Literal

from pydantic import BaseModel, HttpUrl, constr


class TokenRequest(BaseModel):
    client_id: HttpUrl
    client_assertion: constr(regex=r"^[a-zA-Z\_\-0-9]+\.[a-zA-Z\_\-0-9]+\.[a-zA-Z\_\-0-9]+") # noqa: F722
    client_assertion_type: Literal[
        "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
    ]


class TokenAuthnCodeRequest(TokenRequest):
    # TODO: is 1*VSCHAR
    code: str
    # TODO: is 43*128unreserved, where unreserved = ALPHA / DIGIT / "-" / "." / "_" / "~"
    code_verifier: str
    grant_type: Literal["authorization_code"]

    def example():
        return TokenAuthnCodeRequest(
            client_id = "http://example.com",
            client_assertion = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjJIbm9GUzNZbkM5dGppQ2FpdmhXTFZVSjNBeHdHR3pfOTh1UkZhcU1FRXMifQ.eyJpc3MiOiJodHRwOi8vMTI3LjAuMC4xOjgwMDAvb2lkYy9ycC8iLCJzdWIiOiJodHRwOi8vMTI3LjAuMC4xOjgwMDAvb2lkYy9ycC8iLCJhdWQiOlsiaHR0cDovLzEyNy4wLjAuMTo4MDAwL29pZGMvb3AvdG9rZW4vIl0sImlhdCI6MTY0ODQ5NTc1NywiZXhwIjoxNjQ4NDk3NzM3LCJqdGkiOiI0OWE2OGQyMS03NTE1LTRmNDMtODZhZC1hMDNhMWNmNDFmNTgifQ.EaWmmuDhoa8jt_go4zrY5AhTGnljIS1zNwIF-f9eBidAiWPYaKwmXRsRoXrAeybLcJ5E8-7TO1S8jZiCxcElQPdRRvuP9ZsgNhfEqDhZtabkwGBFt4gpQZnFsgGDMAi-v4sTM55VsnIJIMrHPNIckZfL-YhD-FSCtDsqrCkCnucXR58Kfp_SEx3hJvrU-2vcOeNXJBTqs3pHl9jws9GJIf6bZd7vQqTMolCC4zBzUp7yT3OXqMt9uCUhLZzLtpTRW0_-u-KW4h44eHOdEf6ePqiFhjflF9_T6cM-OBqzaK0eVvg6RcasvF3IyxdG-ME5crapAibeePqg_Hy__Q5idQ",
            client_assertion_type = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            code = "bb03ad1f2e838335c1050ae280a64f4e195dbeb17ba8aa2dc6fd99e1c5181fc735be6af10b634fbf0f04f533843e199d0261bf570585ca292cb4fb8857480af5",
            code_verifier = "nd6gJEXzUZApV46u4DmVUfZgBYc2SJsZGkaBftof4gcI95ByALg",
            grant_type = "authorization_code"
        )


class TokenRefreshRequest(TokenRequest):
    grant_type: Literal["refresh_token"]
    refresh_token: str

    def example():
        return TokenRefreshRequest(  # nosec B106
            client_id = "http://example.com",
            client_assertion = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjJIbm9GUzNZbkM5dGppQ2FpdmhXTFZVSjNBeHdHR3pfOTh1UkZhcU1FRXMifQ.eyJpc3MiOiJodHRwOi8vMTI3LjAuMC4xOjgwMDAvb2lkYy9ycC8iLCJzdWIiOiJodHRwOi8vMTI3LjAuMC4xOjgwMDAvb2lkYy9ycC8iLCJhdWQiOlsiaHR0cDovLzEyNy4wLjAuMTo4MDAwL29pZGMvb3AvdG9rZW4vIl0sImlhdCI6MTY0ODQ5NTc1NywiZXhwIjoxNjQ4NDk3NzM3LCJqdGkiOiI0OWE2OGQyMS03NTE1LTRmNDMtODZhZC1hMDNhMWNmNDFmNTgifQ.EaWmmuDhoa8jt_go4zrY5AhTGnljIS1zNwIF-f9eBidAiWPYaKwmXRsRoXrAeybLcJ5E8-7TO1S8jZiCxcElQPdRRvuP9ZsgNhfEqDhZtabkwGBFt4gpQZnFsgGDMAi-v4sTM55VsnIJIMrHPNIckZfL-YhD-FSCtDsqrCkCnucXR58Kfp_SEx3hJvrU-2vcOeNXJBTqs3pHl9jws9GJIf6bZd7vQqTMolCC4zBzUp7yT3OXqMt9uCUhLZzLtpTRW0_-u-KW4h44eHOdEf6ePqiFhjflF9_T6cM-OBqzaK0eVvg6RcasvF3IyxdG-ME5crapAibeePqg_Hy__Q5idQ",
            client_assertion_type = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            refresh_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImRCNjdnTDdjazNURmlJQWY3TjZfN1NIdnFrME1EWU1FUWNvR0dsa1VBQXcifQ.eyJpc3MiOiJodHRwOi8vb3AtdGVzdC9vaWRjL29wLyIsInN1YiI6Imh0dHA6Ly9ycC10ZXN0Lml0L29pZGMvcnAvIiwiZXhwIjoxNjQ4NDk3OTU2LCJpYXQiOjE2NDg0OTU5NzYsImF1ZCI6WyJodHRwOi8vcnAtdGVzdC5pdC9vaWRjL3JwLyJdLCJjbGllbnRfaWQiOiJodHRwOi8vcnAtdGVzdC5pdC9vaWRjL3JwLyIsInNjb3BlIjoib3BlbmlkIn0.yDF6BsFpT1h2JdSxyE3hE8chcF0Lq0OtGzRoZkBbN7otHTvAsTcupT-J6JTHnO817Bp1kllvLkJ5X4p3NeElOL-TbzF1xtX2azpiaxZD4xEGOYsMGkRnLeJP9LWGYbJXEBlAjHMpYW-DhZz3cE3iJvmaehi6sIRsXMPszsDIrt2cYmwFg9KrEc2Ty_qWKdIhzgxq82FEgMk2e2ehez3MTH7KAni2hRmtl32w6uf7_cfW5GlLfDjjVNm2Y9NkmrFeKmX0YUOQWXTts1MhlGfnw9ASgBstgfB5tWWmxF6Sg7ojAnPt_eKH75gcMLhUxj4iif8Aj0QNPzXuJ7VlBH9VAA",
            grant_type = "refresh_token"
        )
