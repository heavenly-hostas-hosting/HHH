#!/bin/bash

# inspired by https://supabase.com/docs/guides/self-hosting/docker#installing-and-running-supabase

SB_DST=./supabase-repository
SHA=671aea0a4af7119131393e3bc2d187bc54c8604a

git init $SB_DST
cd $SB_DST
git remote add origin https://github.com/supabase/supabase

git sparse-checkout init --cone
git sparse-checkout set docker/volumes

git fetch --filter=blob:none origin $SHA
git checkout $SHA

cd ..

cp -r $SB_DST/docker/volumes ./volumes
rm -rf $SB_DST
