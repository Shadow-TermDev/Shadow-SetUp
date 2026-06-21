# 🖤 Shadow-SetUp

Setup automático para Termux — zsh + Oh My Zsh + Powerlevel10k + plugins y dotfiles.

## ✨ Qué incluye

- **zsh** como shell principal
- **Oh My Zsh** con tema Powerlevel10k (classic)
- **Plugins:** `zsh-autosuggestions`, `zsh-syntax-highlighting`, `fzf`, `python`, `git`
- **Herramientas:** `eza`, `bat`, `fd`, `fzf`, `zoxide`, `proot-distro`, `termux-api`
- **Dotfiles:** `.zshrc`, `.p10k.zsh`, `colors.properties`, `termux.properties`
- Saludo kawaii por TTS al abrir la terminal 🎀

## 📁 Estructura

```
Shadow-SetUp/
├── setup.sh                        ← script principal
├── dotfiles/
│   ├── .zshrc
│   ├── .p10k.zsh
│   └── .termux/
│       ├── colors.properties       ← colores (tema Argonaut + cursor verde)
│       └── termux.properties       ← cursor parpadeante 250ms
└── README.md
```

## 🚀 Instalación

```bash
pkg install git -y
git clone https://github.com/Shadow-TermDev/Shadow-SetUp.git ~/Shadow-SetUp
cd ~/Shadow-SetUp
chmod +x setup.sh
bash setup.sh
```

> El script hace backup automático de tus dotfiles actuales antes de sobreescribir.

## 🔧 Post-instalación

1. Reinicia Termux o ejecuta `exec zsh`
2. Si el tema no carga correctamente: `p10k configure`
3. Para proot/Ubuntu: instala opencode manualmente dentro del entorno

## 📝 Notas

- El `.p10k.zsh` se descarga desde este repo automáticamente
- Los colores usan el tema **Argonaut** con cursor `#00ff00`
- El cursor parpadea cada 250ms (configurable en `termux.properties`)
