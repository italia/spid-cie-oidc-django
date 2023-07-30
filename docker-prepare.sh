#!/bin/bash

# Copy your configuration to a separate folder
export EXPFOLDER="examples-docker"
cp -R examples $EXPFOLDER

# remove dev db
rm -f $EXPFOLDER/relying_party/db.sqlite3 
rm -f $EXPFOLDER/provider/db.sqlite3 
rm -f $EXPFOLDER/federation_authority/db.sqlite3 

# Configure the rewrite rules:
export SUB_AT='s,http://127.0.0.1:8000,http://trust-anchor.org:8000,g'
export SUB_RP='s,http://127.0.0.1:8001,http://relying-party.org:8001,g'
export SUB_OP='s,http://127.0.0.1:8002,http://cie-provider.org:8002,g'
export SUB_WTA='s,http://127.0.0.1:8000,http://wallet.trust-anchor.org:8005,g'

# Apply the rewrite rules:

sed -e $SUB_AT -e $SUB_RP -e $SUB_OP examples/federation_authority/dumps/example.json > $EXPFOLDER/federation_authority/dumps/example.json
sed -e $SUB_AT -e $SUB_RP -e $SUB_OP examples/federation_authority/federation_authority/settingslocal.py.example > $EXPFOLDER/federation_authority/federation_authority/settingslocal.py

sed -e $SUB_WTA examples/wallet_trust_anchor/dumps/ta-ec.json > $EXPFOLDER/wallet_trust_anchor/dumps/ta-ec.json
sed -e $SUB_WTA examples/wallet_trust_anchor/wallet_trust_anchor/settingslocal.py.example > $EXPFOLDER/wallet_trust_anchor/wallet_trust_anchor/settingslocal.py

sed -e $SUB_AT -e $SUB_RP -e $SUB_OP examples/relying_party/dumps/example.json > $EXPFOLDER/relying_party/dumps/example.json
sed -e $SUB_AT -e $SUB_RP -e $SUB_OP examples/relying_party/relying_party/settingslocal.py.example > $EXPFOLDER/relying_party/relying_party/settingslocal.py

sed -e $SUB_AT -e $SUB_RP -e $SUB_OP examples/provider/dumps/example.json > $EXPFOLDER/provider/dumps/example.json
sed -e $SUB_AT -e $SUB_RP -e $SUB_OP examples/provider/provider/settingslocal.py.example > $EXPFOLDER/provider/provider/settingslocal.py

