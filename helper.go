//
//	helper.go
//	SCons Go Tools
//
//	Copyright (c) 2010, Ross Light.
//	All rights reserved.
//
//	Redistribution and use in source and binary forms, with or without
//	modification, are permitted provided that the following conditions are met:
//
//		Redistributions of source code must retain the above copyright notice,
//		this list of conditions and the following disclaimer.
//
//		Redistributions in binary form must reproduce the above copyright
//		notice, this list of conditions and the following disclaimer in the
//		documentation and/or other materials provided with the distribution.
//
//		Neither the name of the SCons Go Tools nor the names of its contributors
//		may be used to endorse or promote products derived from this software
//		without specific prior written permission.
//
//	THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
//	AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
//	IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
//	ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
//	LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
//	CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
//	SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
//	INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
//	CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
//	ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
//	POSSIBILITY OF SUCH DAMAGE.
//

package main

import (
	"flag"
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"os"
	"path"
	"runtime"
	"strconv"
	"strings"
	"syscall"
	"unicode"
	"utf8"
)

func buildConfig() (config map[string]string) {
	config = make(map[string]string)
	prefix := getPrefix()
	// Build info
	config["GOOS"] = syscall.OS
	config["GOARCH"] = syscall.ARCH
	config["archname"] = prefix
	// GOROOT-related stuff
	config["GOROOT"] = runtime.GOROOT()
	config["pkgroot"] = path.Join(runtime.GOROOT(), "pkg", syscall.OS+"_"+syscall.ARCH)
	// GOBIN-related stuff
	gobin := getGOBIN()
	config["GOBIN"] = gobin
	config["gc"] = path.Join(gobin, prefix+"g")
	config["ld"] = path.Join(gobin, prefix+"l")
	return
}

func getGOBIN() string {
	if gobin := os.Getenv("GOBIN"); gobin != "" {
		return gobin
	}
	return path.Join(os.Getenv("HOME"), "bin")
}

func getPrefix() string {
	switch syscall.ARCH {
	case "amd64":
		return "6"
	case "386":
		return "8"
	case "arm":
		return "5"
	}
	return ""
}

func printVar(name, value string) {
	fmt.Printf("%s=%s\n", name, value)
}

func extractImports(fileNode *ast.File) <-chan *ast.ImportSpec {
	ch := make(chan *ast.ImportSpec)
	go func() {
		defer close(ch)
		for _, decl := range fileNode.Decls {
			if gd, ok := decl.(*ast.GenDecl); ok && gd.Tok == token.IMPORT {
				for _, spec := range gd.Specs {
					ch <- spec.(*ast.ImportSpec)
				}
			}
		}
	}()
	return ch
}

func extractTests(fileNode *ast.File) <-chan *ast.FuncDecl {
	ch := make(chan *ast.FuncDecl)
	hasPrefix := func(s, prefix string) bool {
		if !strings.HasPrefix(s, prefix) {
			return false
		}
		rune, _ := utf8.DecodeRuneInString(s[len(prefix):])
		return unicode.IsUpper(rune)
	}
	matches := func(name *ast.Ident) bool {
		if !name.IsExported() {
			return false
		}
		n := name.Name
		return hasPrefix(n, "Test") || hasPrefix(n, "Benchmark")
	}
	go func() {
		defer close(ch)
		for _, decl := range fileNode.Decls {
			if fd, ok := decl.(*ast.FuncDecl); ok && fd.Recv == nil && matches(fd.Name) {
				ch <- fd
			}
		}
	}()
	return ch
}

func parseArgs() <-chan *ast.File {
	ch := make(chan *ast.File)
	go func() {
		defer close(ch)
		for _, fname := range flag.Args() {
			fileNode, err := parser.ParseFile(fname, nil, 0)
			if err != nil {
				fmt.Fprintf(os.Stderr, "Error parsing %s: %v\n", fname, err)
				if fileNode == nil {
					continue
				}
			}
			ch <- fileNode
		}
	}()
	return ch
}

func main() {
	var mode string
	var configValue string

	flag.StringVar(&mode, "mode", "config", "Change the mode of the helper")
	flag.StringVar(&configValue, "value", "", "When set, only print a specific configuration value")
	flag.Parse()

	switch mode {
	case "config":
		config := buildConfig()
		if configValue == "" {
			for k, v := range config {
				fmt.Printf("%s=%s\n", k, v)
			}
		} else if v, ok := config[configValue]; ok {
			fmt.Println(v)
		}
	case "imports":
		for fileNode := range parseArgs() {
			for spec := range extractImports(fileNode) {
				importPath, _ := strconv.Unquote(string(spec.Path.Value))
				fmt.Println(importPath)
			}
		}
	case "package":
		for fileNode := range parseArgs() {
			fmt.Println(fileNode.Name.Name)
		}
	case "both":
		for fileNode := range parseArgs() {
			fmt.Printf("package %s\n", fileNode.Name.Name)
			for spec := range extractImports(fileNode) {
				importPath, _ := strconv.Unquote(string(spec.Path.Value))
				fmt.Printf("import %s\n", importPath)
			}
		}
	case "tests":
		for fileNode := range parseArgs() {
			for decl := range extractTests(fileNode) {
				fmt.Printf("%s.%s\n", fileNode.Name.Name, decl.Name.Name)
			}
		}
	default:
		fmt.Fprintf(os.Stderr, "Invalid mode: %s\n", mode)
		os.Exit(1)
	}
}
