# Spec Mockup Design

**Yapay zeka ajanlarına "AI slop" yerine gerçek arayüz tasarlatan bir skill.**
Claude Code, Codex, opencode, Gemini/Antigravity, Cursor, Kiro, Qwen ve `SKILL.md` okuyan her ajanla çalışır.

[English](README.md) · [Canlı demo](https://lunanoir21.github.io/spec-mockup-design/) · MIT lisanslı

![Gezilebilir canvas demosu](assets/canvas-demo.gif)

Bir ajandan "ayarlar ekranı tasarla" istediğinde genelde aynı sayfayı alırsın: mor gradyan, Inter yazı tipi, yuvarlak kartlar,
sol kenar çizgili kutular, lorem ipsum ve tek bir güzel durum. Bu skill onun yerine, insanların gerçekten beğenip kullandığı sonuçları üreten bir iş akışı koyar:

1. **Gerçek referansa dayan.** Projenin kendi kaynağından (veya adı verilen bir üründen) gerçek renk, radius, boşluk ve animasyon sürelerini çıkar. Gerçeği varken uydurma.
2. **Ruh hali değil tasarım dili kur.** Tek cümlelik konsept, OKLCH ile üretilmiş uyumlu palet, ölçek sistemi, tek kalınlıkta ikonlar.
3. **Her durumu göster.** Her gerçek durum için ayrı tahta: boşta, hover, boş, hata, yükleniyor, taşma, devre dışı, odak; ayrıca hareket storyboard'u, font karşılaştırması, tema seçici ve token tahtası.
4. **Slop kapısı.** Bir denetleyici puanlar, teslim fişi dosyaların gerçekten var olduğunu kanıtlar, ekran görüntülerine bakılır.
5. **Canvas teslim et.** Tasarım aracı olmayan ajanlar tek bir HTML **sonsuz canvas** üretir (sürükle, Ctrl+tekerlek ile yakınlaş, tahtaya odaklan, indir). Claude'un Design canvas'ı ile aynı deneyim.

| Genel bakış | Tahtaya odak |
|---|---|
| ![genel](assets/shot-overview.jpg) | ![odak](assets/shot-focus.jpg) |
| ![hava durumu widget](assets/shot-weather.jpg) | ![cpu fan widget](assets/shot-cpu.jpg) |

Dördü de bu skill'i izleyen ücretsiz opencode modelleriyle üretildi. [Canlı demoda](https://lunanoir21.github.io/spec-mockup-design/) kendin gezip yakınlaştırabilirsin.

## Kurulum

```bash
git clone https://github.com/lunanoir21/spec-mockup-design ~/.agents/skills/spec-mockup-design
bash ~/.agents/skills/spec-mockup-design/scripts/install-everywhere.sh
```

`install-everywhere.sh` bulduğu her ajanın skills klasörüne bağlantı koyar (`~/.claude/skills`, `~/.codex/skills`,
`~/.config/opencode/skills`, `~/.gemini/skills`, `~/.cursor/skills`, `~/.kiro/skills`, `~/.qwen/skills` ve diğerleri). Tekrar
çalıştırmak zararsızdır, hiçbir şeyin üstüne yazmaz, silmez (`--dry-run` ne yapacağını gösterir). Skills klasörü olmayan bir
ajan için talimat dosyasına (`AGENTS.md`, `GEMINI.md`...) şu satırı ekle:

> Arayüz tasarımı veya mockup istendiğinde önce `~/.agents/skills/spec-mockup-design/SKILL.md` dosyasını yükle ve uygula.

Gereksinimler: Python 3.8+ (yalnızca standart kütüphane), ekran görüntüleri için Chromium veya Chrome (isteğe bağlı), `bash`.

## Kullanım

Ajanına tasarım iste: "durum çubuğum için CPU sıcaklığı widget'ı tasarla", "ayarlar sayfası için 3 seçenek göster". Skill kendiliğinden devreye girer.
Ajan kısa bir script dizisi çalıştırır (`SKILL.md`'deki "quick path"): `palette.py`, `scales.py`, `new-canvas.py`, `slop-lint.py`, `shoot.sh`, `check-done.py`.

Canvas'ta gezinme: arka planı **sürükle**, **Ctrl+tekerlek** veya sıkıştır ile yakınlaş, **çift tık** hepsini sığdırır,
**F** tahtaya odaklar (ok tuşları sonraki/önceki, **Esc** geri), **0** sığdır, **1** %100, **Tahtalar** listesi ile atla,
tahtanın indirme düğmesi onu tek başına HTML olarak kaydeder. `?only=<id>` tek tahta, `?flat=1` klasik kaydırmalı sayfa, `#<id>` tahtaya odaklı açar.

## İçerik

Dosya yapısı ve her scriptin görevi için [İngilizce README](README.md#what-is-inside) tablosuna bak.

## İşe yarıyor mu?

Ücretsiz opencode modelleriyle 9 gerçek ajan koşusu (istemde skill'in adı geçmeden): 8'inde skill bulunup kullanıldı, 5'i tam puan aldı.
Başarısızlıklar doğrudan düzeltmelere dönüştü (uydurma rapora karşı teslim fişi, boş tahta kuralı, ilk palet tarifini kopyalamaya karşı klişe kuralı). Script testleri 85/85 geçiyor.

Dürüst sınırlar: denetleyici zevki değil varsayılanları ölçer, ekran görüntülerine bakmak gerekir. Kalite modele bağlı; bazı modeller erken bırakıyor veya çok uzun cilalıyor.

## Katkı

Sorun ve PR'lar açık, bkz. [CONTRIBUTING.md](CONTRIBUTING.md). Değişiklikten önce `python3 tests/selftest.py` çalıştır.

## Lisans

[MIT](LICENSE)
