/* SPDX-License-Identifier: MPL-2.0 */
#include <windows.h>
#include <psapi.h>
#include <cwchar>
#include <iostream>
#include <string>
#include <vector>

int wmain(int argc, wchar_t** argv) {
  if (argc < 3) return 2;
  std::wstring root(argv[1]);
  PROCESS_MITIGATION_IMAGE_LOAD_POLICY policy{};
  policy.PreferSystem32Images = 1;
  if (!SetProcessMitigationPolicy(ProcessImageLoadPolicy, &policy, sizeof(policy))) return 3;
  // This executable is linked with the static CRT. Preload the reviewed local
  // runtime using absolute paths, then resolve the real xul.dll imports against
  // those libraries. No system files or Firefox security policies are changed.
  for (int i = 2; i < argc; ++i) {
    std::wstring path = root + L"\\" + argv[i];
    if (!LoadLibraryExW(path.c_str(), nullptr,
                        LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR | LOAD_LIBRARY_SEARCH_SYSTEM32)) {
      std::wcerr << L"Load failed: " << argv[i] << L" error " << GetLastError() << L"\n";
      return 4;
    }
  }
  std::wstring xul = root + L"\\xul.dll";
  if (!LoadLibraryExW(xul.c_str(), nullptr,
                      LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR | LOAD_LIBRARY_SEARCH_SYSTEM32)) {
    std::wcerr << L"xul.dll dependency load failed: " << GetLastError() << L"\n";
    return 5;
  }
  HMODULE modules[512];
  DWORD bytes = 0;
  if (!EnumProcessModules(GetCurrentProcess(), modules, sizeof(modules), &bytes) || bytes > sizeof(modules)) return 6;
  for (int i = 2; i < argc; ++i) {
    bool found = false;
    for (DWORD j = 0; j < bytes / sizeof(HMODULE); ++j) {
      wchar_t path[2048];
      DWORD length = GetModuleFileNameW(modules[j], path, 2048);
      if (!length || length >= 2048) return 7;
      const wchar_t* slash = std::wcsrchr(path, L'\\');
      const wchar_t* name = slash ? slash + 1 : path;
      if (_wcsicmp(name, argv[i]) != 0) continue;
      std::wstring expected = root + L"\\" + argv[i];
      if (_wcsicmp(path, expected.c_str()) != 0) {
        std::wcerr << L"Unexpected system CRT dependency: " << path << L"\n";
        return 8;
      }
      found = true;
      std::wcout << argv[i] << L"|" << path << L"\n";
    }
    if (!found) return 9;
  }
  return 0;
}
