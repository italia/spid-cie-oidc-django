# Create a jws

Enter in your project shell

````
./manage.py shell
````
Define a jwk, for example:
````
jwk=
{
    'kty': 'RSA', 
    'kid': 'FifYx03bnosD8m6gYQIfNHNP9cM_Sam9Tc5nLloIIrc', 
    'e': 'AQAB', 
    'n':'3i5vV-_4nF_ES1BU86Zf2Bj6SiyGdGM3Izc2GrvtknQQCzpT3QlGv2d_wMrzVTS7PmZlvjyi2Qceq8EmEwbsIa5R8G57fxSpE0HL33giJfhpe8ublY4hGb6tEqSbHiFcgiF4T-Ft_98pz4nZtKTcesMZ8CcDUd9ibaLXGM4vaiUhSt76X1qOzqJHqAKMG-9VGm5DD2GSe7cu1yvaMCMPU6DGOqHYoBSkSbsnLelsRg6sINh6mZfb39odTJlOMFGhlg665702kc_iqqxd8jpyOh94vBagmJB4EQqI1qEte8sTMeBkVRpSLDoV5uNTlp2ZdINu1SakmaHB3WeStwC1lw', 'd':'QvPRP7mjvFOrjlp9zxJyzWbxfYqfVdFUGzuXBUVeWQS6lPeVsAUMmb8xo0JFQ4bpaetne4VAOZBIsM86jv9GBvxF2uMgOfJa5N-t9QB5oeGSv-hiURYMaXqpIvYRfGnnO5ukasXu5O0150GOJj6L5j6GwXSwLmrXeVxZ3zK63QwVl71xU1LR-lO0wLbqQROIT37Jw72B__wBk3QC0HjbrPv1fUVxKB3RCDR43X7PQkMPOfRHxicyp2MA4mLhLvuoRTTI4dfnd8Ou-xX5ctVzYmL0EMxPCleDFDIn9gTxpgCH95sVi-Zg6Zw5k1J_cchoD4AgGSSt2dr9mbiTRjLlcQ', 'p':'8BHX7hErQjESybgfzcX0hZmM-e1EWaM76uNJop9BiqRlBz9f-XxuC40A032AaZFDXqxVi3W0Hn1vJA6lSj9mGY5HEY-YVWAdOLLjM12oQ_cnH6czElExAoppUeMWsDEewDbZTn6rX5silcZ8Pu7Tsj-KSjPVzl9dr1w76EzsYj8', 
    'q':'7Oy3PGm3MjVlgTlgHnRKC-IcoB50hCBiqwACVcnlIgpg9Kt_srV7NWdmo5DJFIdrrvkjmN4wi9IOknSymStU-sB8BepnnterjPyBOr9PbttUP13qcOjuvjzD7Tr0IGou3yhA-YOuO9hOluhqd4tJIkdxT_X9qxgFQx5NSnsBpqk'
}
````
or create a new one:
````
from spid_cie_oidc.entity.jwks import create_jwk

jwk = create_jwk()
````
Define a payload for example:

````
payload=
{
    'client_id': 'https://rp.cie.it', 
    'response_type': 'code', 
    'scope': 'openid', 
    'code_challenge': 'qWJlMe0xdbXrKxTm72EpH659bUxAxw80', 
    'code_challenge_method': 'S256', 
    'nonce': 'MBzGqyf9QytD28eupyWhSqMj78WNqpc2', 
    'prompt': 'consent login', 
    'redirect_uri': 'https://rp.cie.it/callback1', 
    'acr_values': 'CIE_L1 CIE_L2', 
    'claims': {
        'id_token': {
            'family_name': {'essential': True}, 
            'email': {'essential': True}
        }, 
        'userinfo': {
            'name': None, 
            'family_name': None
            }
    }, 
    'state': 'fyZiOL9Lf2CeKuNT2JzxiLRDink0uPcd'}
````

Then
````
from spid_cie_oidc.entity.jwtse import create_jws
create_jws(payload,jwk)
````

`create_jws(payload,jwk)` returns jws as follows:

````
'eyJhbGciOiJSUzI1NiIsImtpZCI6IkZpZll4MDNibm9zRDhtNmdZUUlmTkhOUDljTV9TYW05VGM1bkxsb0lJcmMifQ.eyJjbGllbnRfaWQiOiJodHRwczovL3JwLmNpZS5pdCIsInJlc3BvbnNlX3R5cGUiOiJjb2RlIiwic2NvcGUiOiJvcGVuaWQiLCJjb2RlX2NoYWxsZW5nZSI6InFXSmxNZTB4ZGJYckt4VG03MkVwSDY1OWJVeEF4dzgwIiwiY29kZV9jaGFsbGVuZ2VfbWV0aG9kIjoiUzI1NiIsIm5vbmNlIjoiTUJ6R3F5ZjlReXREMjhldXB5V2hTcU1qNzhXTnFwYzIiLCJwcm9tcHQiOiJjb25zZW50IGxvZ2luIiwicmVkaXJlY3RfdXJpIjoiaHR0cHM6Ly9ycC5jaWUuaXQvY2FsbGJhY2sxLyIsImFjcl92YWx1ZXMiOiJDSUVfTDEgQ0lFX0wyIiwiY2xhaW1zIjp7ImlkX3Rva2VuIjp7ImZhbWlseV9uYW1lIjp7ImVzc2VudGlhbCI6dHJ1ZX0sImVtYWlsIjp7ImVzc2VudGlhbCI6dHJ1ZX19LCJ1c2VyaW5mbyI6eyJuYW1lIjpudWxsLCJmYW1pbHlfbmFtZSI6bnVsbH19LCJzdGF0ZSI6ImZ5WmlPTDlMZjJDZUt1TlQySnp4aUxSRGluazB1UGNkIn0.x5E2S55W1_Sh6xzBNRjaYr7rhI0vIqLhZBlG7XtimL60IgZHe9IdrDwGFzY6jezT8j_poxppGAP5j7HJYGKkrzhLJHKSQyIlgeWXDy5FEBAJstcV6fCSRIeeuPhnNOT-pGGCI1p_WBKolztmv_EfILoDsY9MiKAe87k_2DOxRCcYzIwRUSZGoyb8g59t6oDylugelDNxG9-27rPth8k7suoJZiTc9zZ4U3wAOqlkPX0BfhtYPYATI6jZfftwQJYb2Rm081Pml5A_G7DIUO10k5_jDzaL_yna85AFBjuEfy5NqQhe4OTqGmN5xq_iv8c06m6tLyxraXQZSfC4_4fheQ'
````

# Verify a jws

Enter in your project shell

````
./manage.py shell
````

Create a jwk

````
from spid_cie_oidc.entity.jwks import create_jwk

jwk = create_jwk()
````
Then verify 

````
from spid_cie_oidc.entity.jwtse  import verify_jws
verify_jws(jws, jwk)
````

# How to obtain head from a jws

Enter in your project shell

````
./manage.py shell
````
Create a jws as described above, then
````
from spid_cie_oidc.entity.jwtse import unpad_jwt_head
unpad_jwt_head(jws)
````

# How to obtain payload from a jws

Enter in your project shell

````
./manage.py shell
````
Create a jws as described above, then
````
from spid_cie_oidc.entity.jwtse import unpad_jwt_payload
unpad_jwt_payload(jws)
````
