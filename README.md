brew install oath-toolkit

oathtool -totp $(cat key.hex)

echo -e "Oathtool: \033[1;32m$(oathtool --totp $(cat key.hex))\033[0m | Mi ft_otp: \033[1;36m$(./ft_otp -k ft_otp.key)\033[0m"