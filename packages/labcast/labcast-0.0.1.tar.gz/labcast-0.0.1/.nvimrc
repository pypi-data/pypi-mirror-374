function! s:insert_license_slash()
  set formatoptions-=cro
  execute "normal! i// -----------------------------------------------------------------------------"
  execute "normal! o// SPDX-License-Identifier: Apache-2.0"
  execute "normal! o// Copyright (C) 2025 Jayesh Badwaik <j.badwaik@fz-juelich.de>"
  execute "normal! o// -----------------------------------------------------------------------------"
  normal! o
  set formatoptions+=cro
endfunction

function! s:insert_license_hash()
  set formatoptions-=cro
  execute "normal! i# ------------------------------------------------------------------------------"
  execute "normal! o# SPDX-License-Identifier: Apache-2.0"
  execute "normal! o# Copyright (C) 2025 Jayesh Badwaik <j.badwaik@fz-juelich.de>"
  execute "normal! o# ------------------------------------------------------------------------------"
  set formatoptions+=cro
endfunction

function! s:insert_license_percent()
  set formatoptions-=cro
  execute "normal! i% ------------------------------------------------------------------------------"
  execute "normal! o% SPDX-License-Identifier: Apache-2.0"
  execute "normal! o% Copyright (C) 2025 Jayesh Badwaik <j.badwaik@fz-juelich.de>"
  execute "normal! o% ------------------------------------------------------------------------------"
  set formatoptions+=cro
endfunction


function! s:insert_license_quote()
  set formatoptions-=cro
  execute "normal! i\" -----------------------------------------------------------------------------"
  execute "normal! o\" SPDX-License-Identifier: Apache-2.0"
  execute "normal! o\" Copyright (C) 2025 Jayesh Badwaik <j.badwaik@fz-juelich.de>"
  execute "normal! o\" -----------------------------------------------------------------------------"
  set formatoptions+=cro
endfunction

function! s:insert_license_html()
  set formatoptions-=cro
  execute "normal! i<!--"
  execute "normal! o- SPDX-License-Identifier: Apache-2.0"
  execute "normal! o- Copyright (C) 2025 Jayesh Badwaik <j.badwaik@fz-juelich.de>"
  execute "normal! o-->"
  set formatoptions+=cro
endfunction

function! Insert_license_slash()
  execute "normal! O"
  call s:insert_license_cpp()
endfunction

function! Insert_license_hash()
  execute "normal! O"
  call s:insert_license_hash()
endfunction

function! Insert_license_percent()
  execute "normal! O"
  call s:insert_license_percent()
endfunction

function! Insert_license_quote()
  execute "normal! O"
  call s:insert_license_quote()
endfunction

function! Insert_license_html()
  execute "normal! O"
  call s:insert_license_html()
endfunction

autocmd BufNewFile *.{cuh}          call <SID>insert_license_slash()
autocmd BufNewFile *.{cuhpp}        call <SID>insert_license_slash()
autocmd BufNewFile *.{h}            call <SID>insert_license_slash()
autocmd BufNewFile *.{c}            call <SID>insert_license_slash()
autocmd BufNewFile *.{hpp}          call <SID>insert_license_slash()
autocmd BufNewFile *.{cpp}          call <SID>insert_license_slash()
autocmd BufNewFile *.{cu}           call <SID>insert_license_slash()
autocmd BufNewFile *.{ipp}          call <SID>insert_license_slash()
autocmd BufNewFile *.{rs}           call <SID>insert_license_slash()

autocmd BufNewFile CMakeLists.txt   call <SID>insert_license_hash()
autocmd BufNewFile *.cmake          call <SID>insert_license_hash()
autocmd BufNewFile *.{sh}           call <SID>insert_license_hash()
autocmd BufNewFile *.{py}           call <SID>insert_license_hash()
autocmd BufNewFile *.{toml}           call <SID>insert_license_hash()
autocmd BufNewFile *.{yml}           call <SID>insert_license_hash()

autocmd BufNewFile *.{md} call <SID>insert_license_html()

autocmd BufNewFile *.{tex} call <SID>insert_license_percent()
autocmd BufNewFile *.{sty} call <SID>insert_license_percent()
autocmd BufNewFile *.{cls} call <SID>insert_license_percent()

" Remove Trailing Whitespace on Save
autocmd BufWritePre * %s/\s\+$//e

" Show trailing whitespace:
highlight ExtraWhitespace ctermbg=red guibg=red
autocmd ColorScheme * highlight ExtraWhitespace ctermbg=red guibg=red
match ExtraWhitespace /\s\+$/

function! Insert_header_guard()
  execute "normal! O"
  call s:insert_header_guard()
endfunction


autocmd BufNewFile *.{cuh}          call <SID>insert_header_guard()
autocmd BufNewFile *.{cuhpp}        call <SID>insert_header_guard()
autocmd BufNewFile *.{h}            call <SID>insert_header_guard()
autocmd BufNewFile *.{hpp}          call <SID>insert_header_guard()
autocmd BufNewFile *.{hip}          call <SID>insert_header_guard()

" Automatic C / C++ header guards
function! s:insert_header_guard()
  set formatoptions-=cro
  let gatename_0 = substitute(substitute(toupper(@%), "\\.", "_", "g"), "/", "_", "g")
  let gatename_1 = substitute(gatename_0, "SRC_INCLUDE_", "", "g")
  let gatename_2 = substitute(gatename_1, "TEST_COMMON_INCLUDE_", "", "g")
  let gatename_3 = substitute(gatename_2, "BENCH_COMMON_INCLUDE_", "", "g")
  let gatename = gatename_3
  execute "normal! o#ifndef " . gatename
  execute "normal! o#define " . gatename
  normal! o
  execute "normal! Go#endif // " . gatename
  set formatoptions-=cro
  normal! k
endfunction
