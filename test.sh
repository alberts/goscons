#!/bin/bash
set -xe

rm -rf prj[1234]/bin
rm -rf prj[1234]/pkg

scons -C prj1 -f SConstruct -c
scons -C prj1 -f SConstruct --random -j16
scons -C prj1 -f SConstruct test
scons -C prj1 -f SConstruct test_pkg1
scons -C prj1 -f SConstruct test_pkg2
scons -C prj1 -f SConstruct bench
scons -C prj1 -f SConstruct bench_pkg1
scons -C prj1 -f SConstruct bench_pkg2
scons -C prj1 -f SConstruct -c
scons -C prj1 -f SConstruct test
scons -C prj1 -f SConstruct -c
scons -C prj1 -f SConstruct test_pkg1
scons -C prj1 -f SConstruct -c
scons -C prj1 -f SConstruct bench
scons -C prj1 -f SConstruct -c
scons -C prj1 -f SConstruct bench_pkg1
scons -C prj1 -f SConstruct -c
scons -C prj1 -f SConstruct bench_pkg2
CRASH=1 scons -C prj1 -f SConstruct test || true
scons -C prj1 -f SConstruct --random
scons -C prj1 -f SConstruct.386 -c
scons -C prj1 -f SConstruct.386 --random -j16

scons -C prj2 -f SConstruct -c
scons -C prj2 -f SConstruct --random -j16
scons -C prj2 -f SConstruct.386 -c
scons -C prj2 -f SConstruct.386 --random -j16

# check that GoDep from prj2->prj1 builds prj1
scons -C prj2 -f SConstruct -c
scons -C prj1 -f SConstruct -c
scons -C prj2 -f SConstruct --random -j16
scons -C prj2 -f SConstruct.386 -c
scons -C prj1 -f SConstruct.386 -c
scons -C prj2 -f SConstruct.386 --random -j16

scons -C prj3 -f SConstruct -c
scons -C prj3 -f SConstruct --random -j16

scons -C prj4 -f SConstruct -c
scons -C prj4 -f SConstruct --random -j16
scons -C prj4 -f SConstruct test_bar_time

scons -C prj5 -f SConstruct -c
scons -C prj5 -f SConstruct
scons -C prj5 -f SConstruct test
