#!/bin/bash
set -xe
scons -C prj1 -f SConstruct -c
scons -C prj1 -f SConstruct
scons -C prj1 -f SConstruct.386 -c
scons -C prj1 -f SConstruct.386
scons -C prj2 -f SConstruct -c
scons -C prj2 -f SConstruct
scons -C prj2 -f SConstruct.386 -c
scons -C prj2 -f SConstruct.386
scons -C prj3 -f SConstruct -c
scons -C prj3 -f SConstruct
file prj1/bin/*/*
ldd prj1/bin/*/*
file prj2/bin/*/*
ldd prj2/bin/*/*
file prj3/main
ldd prj3/main
