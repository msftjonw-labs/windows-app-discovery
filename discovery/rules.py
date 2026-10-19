"""Shared, versioned evidence rules for the pilot classifiers."""

import re

RULESET_VERSION = "pilot-3"
OS_TARGETS = {"Windows", "Linux", "Android", "iOS", "macOS", "BSD"}

# These are indicators, not proofs of runtime behavior or supported platforms.
RULES = [
    ("windows-target", "platform", "Windows",
     r"net[0-9.]+-windows|<UseWindowsForms>\s*true|<UseWPF>\s*true|Microsoft\.WindowsAppSDK|System\.Windows\.Forms|#\s*include\s*[<\"]windows\.h"),
    ("linux-target", "platform", "Linux", r"linux-gnu|linux-musl|linuxdeploy|org\.freedesktop\.Platform"),
    ("android-target", "platform", "Android", r"com\.android\.application|net[0-9.]+-android|<manifest[^>]+xmlns:android"),
    ("ios-target", "platform", "iOS", r"net[0-9.]+-ios|IPHONEOS_DEPLOYMENT_TARGET|iphoneos|import\s+UIKit"),
    ("macos-target", "platform", "macOS", r"net[0-9.]+-maccatalyst|MACOSX_DEPLOYMENT_TARGET|import\s+AppKit"),
    ("web-target", "platform", "Web", r'"(?:react-dom|next|@angular/core|vue)"\s*:|Microsoft\.NET\.Sdk\.Web'),
    ("bsd-target", "platform", "BSD", r"target_os\s*=\s*\"(?:freebsd|openbsd|netbsd)\"|CMAKE_SYSTEM_NAME\s+FreeBSD"),
    ("backend", "platform", "Server / backend", r'"(?:express|fastify|@nestjs/core|koa|hono)"\s*:|from\s+(?:fastapi|flask|django)\b|Microsoft\.NET\.Sdk\.Web|org\.springframework\.boot'),
    ("wasm", "platform", "WebAssembly", r"wasm32-(?:unknown|wasi)|wasm_bindgen|wasm-bindgen"),
    ("embedded", "platform", "Embedded / firmware", r"\bESP_PLATFORM\b|#\s*include\s*[<\"]Arduino\.h|zephyr_library\s*\("),
    ("contracts", "platform", "Smart contracts", r"\bsoroban[-_]sdk\b|\banchor[-_]lang\b|pragma\s+solidity\b|@openzeppelin/contracts"),
    ("winforms", "framework", "Windows Forms", r"<UseWindowsForms>\s*true|System\.Windows\.Forms"),
    ("wpf", "framework", "WPF", r"<UseWPF>\s*true|System\.Windows\.(?:Controls|Application)\b"),
    ("winui", "framework", "WinUI / Windows App SDK", r"Microsoft\.WindowsAppSDK|Microsoft\.UI\.Xaml"),
    ("uwp", "framework", "UWP", r"Microsoft\.NETCore\.UniversalWindowsPlatform|Windows\.UI\.Xaml"),
    ("electron", "framework", "Electron", r'"electron"\s*:'),
    ("avalonia", "framework", "Avalonia", r'Include\s*=\s*"Avalonia(?:\.Desktop)?"|using\s+Avalonia'),
    ("maui", "framework", ".NET MAUI", r"<UseMaui>\s*true|Microsoft\.Maui\.Controls"),
    ("flutter", "framework", "Flutter", r"flutter:\s*\n\s+sdk:\s*flutter|package:flutter/"),
    ("qt", "framework", "Qt", r"find_package\s*\(\s*Qt[56]|#\s*include\s*[<\"]QApplication"),
    ("react-native", "framework", "React Native", r'"react-native"\s*:'),
    ("react", "framework", "React", r'"react"\s*:|from\s+["\']react["\']'),
    ("next", "framework", "Next.js", r'"next"\s*:|from\s+["\']next/'),
    ("vue", "framework", "Vue", r'"vue"\s*:|from\s+["\']vue["\']'),
    ("angular", "framework", "Angular", r'"@angular/core"\s*:'),
    ("svelte", "framework", "Svelte", r'"svelte"\s*:|from\s+["\']svelte'),
    ("express", "framework", "Express", r'"express"\s*:|require\s*\(["\']express["\']\)'),
    ("nestjs", "framework", "NestJS", r'"@nestjs/core"\s*:'),
    ("fastapi", "framework", "FastAPI", r"from\s+fastapi\s+import|\bFastAPI\s*\("),
    ("django", "framework", "Django", r"from\s+django\b|\bdjango\.setup\s*\("),
    ("flask", "framework", "Flask", r"from\s+flask\s+import|\bFlask\s*\(__name__"),
    ("spring", "framework", "Spring Boot", r"org\.springframework\.boot"),
    ("win32", "component", "Win32",
     r'#\s*include\s*[<"]windows\.h|\b(?:CreateWindowEx[AW]?|RegisterClassEx[AW]?|DefWindowProc[AW]?|GetMessage[AW]?)\s*\(|DllImport\s*\(\s*"(?:user32|kernel32|gdi32)(?:\.dll)?"'),
    ("com", "component", "COM",
     r"\b(?:CoCreateInstance|CoInitializeEx|CoInitialize|CoUninitialize|CLSIDFromProgID)\s*\(|\bComImport\b|\bCComPtr\s*<"),
    ("winrt", "component", "WinRT", r"\bwinrt::|Windows\.Foundation\b|\bRoInitialize\s*\("),
    ("pinvoke", "component", ".NET native interop", r"\b(?:DllImport|LibraryImport)\s*\("),
    ("directx", "component", "DirectX", r"\b(?:D3D11CreateDevice|D3D12CreateDevice|Direct3DCreate9)\s*\(|#\s*include\s*[<\"]d3d(?:9|11|12)\.h"),
    ("shell", "component", "Windows Shell", r"\b(?:SHGetKnownFolderPath|SHGetFolderPath[AW]?|ShellExecuteEx[AW]?)\s*\("),
    ("service", "component", "Windows services", r"\b(?:StartServiceCtrlDispatcher[AW]?|RegisterServiceCtrlHandler[AW]?)\s*\(|\bUseWindowsService\s*\(|System\.ServiceProcess"),
    ("registry", "component", "Windows Registry", r"\bReg(?:OpenKeyEx|SetValueEx|QueryValueEx)[AW]?\s*\(|Microsoft\.Win32\.Registry\b"),
]

COMPILED = [(key, kind, label, re.compile(pattern, re.I)) for key, kind, label, pattern in RULES]
COMPONENTS = [label for _, kind, label, _ in RULES if kind == "component"]

# Precedence used to assign each complete repository exactly ONE primary category, so the
# headline distributions are mutually exclusive and sum to 100%. All detected labels stay
# available per repository. Explicit OS targets win over runtimes; specific deployment
# environments win over generic language runtimes; tooling/scripts come last.
ENVIRONMENT_PRECEDENCE = [
    "Embedded / firmware", "Smart contracts", "WebAssembly", "Web", "Server / backend",
    "Cloud / infrastructure", "Containers / Kubernetes", ".NET runtime (OS unspecified)",
    "JVM (OS unspecified)", "Native code (OS unspecified)", "Python runtime (OS unspecified)",
    "PHP runtime (OS unspecified)", "Node.js tooling/runtime (OS unspecified)",
    "Shell / automation (OS unspecified)",
]
# Most specific application framework first (e.g. Next.js and React Native before React).
FRAMEWORK_PRECEDENCE = [
    "Windows Forms", "WPF", "WinUI / Windows App SDK", "UWP", ".NET MAUI", "Avalonia", "Flutter",
    "Electron", "React Native", "Qt", "Next.js", "Angular", "Svelte", "Vue", "React",
    "NestJS", "Spring Boot", "Django", "FastAPI", "Flask", "Express",
]


def _first(labels, precedence):
    ranked = [label for label in precedence if label in labels]
    return ranked[0] if ranked else (sorted(labels)[0] if labels else None)


def primary_platform(platforms):
    """One mutually exclusive platform category for a repository's detected platform labels."""
    labels = set(platforms or []) - {"Unknown"}
    targets = labels & OS_TARGETS
    if len(targets) == 1:
        return next(iter(targets))
    if targets:
        return "Multiple OS (incl. Windows)" if "Windows" in targets else "Multiple OS (no Windows)"
    return _first(labels, ENVIRONMENT_PRECEDENCE) or "Unknown"


def primary_framework(frameworks):
    labels = set(frameworks or []) - {"Unknown"}
    return _first(labels, FRAMEWORK_PRECEDENCE) or "No framework detected"
FILE_RULES = [
    ("browser-files", "Web", r"\.(?:html?|css|scss|sass|vue|svelte|astro|mdx)$", r"\S"),
    ("python-runtime", "Python runtime (OS unspecified)", r"\.(?:py|pyw)$|(?:^|/)(?:pyproject\.toml|requirements[^/]*\.txt)$", r"\S"),
    ("node-runtime", "Node.js tooling/runtime (OS unspecified)", r"(?:^|/)(?:package|deno)\.jsonc?$", r'"(?:dependencies|devDependencies|engines|bin|imports)"\s*:'),
    ("dotnet-runtime", ".NET runtime (OS unspecified)", r"\.(?:csproj|fsproj|vbproj|props)$", r"<TargetFrameworks?>\s*net"),
    ("native-runtime", "Native code (OS unspecified)", r"(?:^|/)(?:Cargo\.toml|go\.mod|CMakeLists\.txt)$", r"(?m)^\s*(?:\[package\]|module\s|project\s*\(|add_executable\s*\()"),
    ("jvm-runtime", "JVM (OS unspecified)", r"(?:^|/)(?:pom\.xml|build\.gradle(?:\.kts)?)$", r"java|kotlin|springframework|jvm"),
    ("php-runtime", "PHP runtime (OS unspecified)", r"\.php$", r"<\?php"),
    ("shell-runtime", "Shell / automation (OS unspecified)", r"\.(?:sh|bash|zsh|ps1|psm1|psd1|nu|bat|cmd)$", r"\S"),
    ("cloud-infra", "Cloud / infrastructure", r"\.(?:tf|bicep)$", r"\b(?:resource|provider|module)\b"),
    ("container", "Containers / Kubernetes", r"(?:^|/)(?:Dockerfile(?:\.[^/]+)?|Containerfile)$", r"(?m)^\s*FROM\s+"),
    ("compose", "Containers / Kubernetes", r"(?:^|/)(?:docker-)?compose[^/]*\.ya?ml$", r"(?m)^\s*services\s*:"),
    ("kubernetes", "Containers / Kubernetes", r"\.ya?ml$", r"(?s)\bapiVersion\s*:.+?\bkind\s*:\s*(?:Deployment|Pod|Service|StatefulSet|DaemonSet|Job|CronJob)\b"),
]
COMPILED_FILE_RULES = [
    (key, label, re.compile(path, re.I), re.compile(pattern, re.I))
    for key, label, path, pattern in FILE_RULES
]
EXCLUDED_DIRS = {
    ".git", ".github", "node_modules", "vendor", "third_party", "thirdparty",
    ".nuget", ".cache", "bin", "obj", "dist", "build", "generated", "__pycache__",
    "tests", "test", "samples", "examples",
    "__tests__", "testfixture", "fixtures", "testdata", "datasets", "_vendor",
    "extlib", "docs", "doc", "documentation", ".venv", "venv", "coverage",
    ".next", ".nuxt", "storybook-static",
}
EXTENSIONS = {
    ".cs", ".csproj", ".vb", ".vbproj", ".fs", ".fsproj", ".props", ".targets",
    ".cpp", ".c", ".h", ".hpp", ".vcxproj", ".xaml", ".xml", ".manifest",
    ".json", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".py", ".rs", ".toml",
    ".go", ".java", ".kt", ".kts", ".gradle", ".swift", ".m", ".mm",
    ".yml", ".yaml", ".txt", ".pro", ".cmake", ".pbxproj", ".dart", ".plist",
    ".html", ".htm", ".css", ".scss", ".sass", ".vue", ".svelte", ".astro", ".mdx",
    ".sh", ".bash", ".zsh", ".ps1", ".psm1", ".psd1", ".nu", ".bat", ".cmd",
    ".tf", ".hcl", ".bicep", ".sol", ".php", ".rb", ".ex", ".exs", ".ino",
    ".pyw", ".jsonc",
}
EXTENSIONLESS_NAMES = {"dockerfile", "containerfile", "makefile", "gemfile", "rakefile"}
JSON_MANIFEST = re.compile(
    r"^(?:package|composer|deno|angular|app|manifest|global|host|"
    r"tsconfig(?:\.[\w-]+)?|jsconfig(?:\.[\w-]+)?|appsettings(?:\.[\w-]+)?)\.jsonc?$",
    re.I,
)
GENERATED_NAMES = {
    "package-lock.json", "npm-shrinkwrap.json", "pnpm-lock.yaml", "yarn.lock",
    "composer.lock", "cargo.lock", "poetry.lock", "uv.lock", "pipfile.lock",
    "gemfile.lock", "packages.lock.json", "project.assets.json", ".pnp.cjs",
}


def inspector_rules():
    """Use the same patterns in Microsoft's engine for Windows characterization."""
    return [
        {
            "id": f"PILOT_{key}", "name": label,
            "description": f"Pilot {kind} indicator for {label}; not semantic proof.",
            "tags": [f"Pilot.{kind}.{key}"], "severity": "Moderate",
            "patterns": [{"pattern": pattern, "type": "Regex",
                          "modifiers": ["i"], "confidence": "High"}],
        }
        for key, kind, label, pattern in RULES if kind in {"component", "framework"}
    ]
