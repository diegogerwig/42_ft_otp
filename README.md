brew install oath-toolkit

oathtool -totp $(cat key.hex)

