# Auftrag: vfio-pci-Bindung für die iGPU dauerhaft machen

## Stand
Das GPU-Passthrough funktioniert. Die Intel Arc 140T läuft in VM 106 ohne Fehler.
Eingebunden über `args`:

```
-device vfio-pci,host=0000:00:02.0,bus=pcie.0,addr=0x2,romfile=/usr/share/kvm/igd.rom,x-igd-opregion=on
```

Maschinentyp q35, `vga: std`. **An dieser VM-Konfiguration bitte nichts ändern.**

## Aufgabe
Dafür sorgen, dass die GPU nach dem nächsten Neustart des Hosts **automatisch an vfio-pci gebunden** wird.
Ohne `hostpci0` macht Proxmox das nicht mehr selbst.

**Keinen Neustart des Hosts auslösen und keine VM stoppen.**

### 1. Sichern
```bash
mkdir -p /root/backup_vfio_$(date +%F)
cp -a /etc/modprobe.d /etc/pve/qemu-server/106.conf /root/backup_vfio_$(date +%F)/
cp /etc/kernel/cmdline /root/backup_vfio_$(date +%F)/ 2>/dev/null
cp /etc/default/grub /root/backup_vfio_$(date +%F)/ 2>/dev/null
cp /etc/modules /root/backup_vfio_$(date +%F)/
```

### 2. Ist-Zustand zeigen
- `cat /etc/modprobe.d/*.conf`
- `cat /etc/kernel/cmdline` bzw. `grep CMDLINE /etc/default/grub`
- Welcher Bootloader wird verwendet: `proxmox-boot-tool status`

Reste aus früheren Versuchen (alte vfio-Einträge, `xe.force_probe`, Blacklists) bitte **auflisten, nicht selbst entfernen**.

### 3. Anlegen: `/etc/modprobe.d/vfio-igpu.conf`
```
options vfio-pci ids=8086:7d51
softdep xe pre: vfio-pci
softdep i915 pre: vfio-pci
```
Bei doppelten oder widersprüchlichen Einträgen in anderen Dateien **vorher nachfragen**.

### 4. vfio-Module in die Initramfs
`/etc/modules` sollte enthalten (bei Bedarf ergänzen):
```
vfio
vfio_iommu_type1
vfio_pci
```
Dann:
```bash
update-initramfs -u -k all
proxmox-boot-tool refresh
```
Kontrollieren:
```bash
lsinitramfs /boot/initrd.img-$(uname -r) | grep -E 'vfio|modprobe.d/vfio-igpu'
```

### 5. Rückweg dokumentieren
Falls der Host nach dem nächsten Neustart nicht sauber hochkommt:
1. Einmalig im Bootmenü an die Kernel-Zeile `module_blacklist=vfio_pci` anhängen und booten.
2. Die Sicherung aus Schritt 1 zurückspielen (`/etc/modprobe.d`, `/etc/modules`).
3. `update-initramfs -u -k all` und `proxmox-boot-tool refresh`.

### 6. Zusammenfassung zeigen
- Welche Dateien wurden geändert?
- Diff gegenüber der Sicherung
- Ausgabe aus Schritt 4

## Außerdem
- Funktionierenden Stand sichern:
  ```bash
  cp /etc/pve/qemu-server/106.conf /root/106.conf.GPU_FUNKTIONIERT
  ```
- Bei VM 106 **`onboot` noch auf 0 lassen**, bis ein Neustart des Hosts bestätigt hat, dass die vfio-Bindung greift.
- Für den SSH-Zugang von Windows zum Host einen **SSH-Schlüssel** einrichten (ed25519, Login per Schlüssel testen) und **keine Passwörter mehr in Befehlen** verwenden. Das root-Passwort ändere ich danach selbst.

## Nach dem nächsten (geplanten) Neustart des Hosts prüfen
```bash
lspci -nnk -s 00:02.0      # erwartet: Kernel driver in use: vfio-pci
qm start 106
```
Danach im Windows-Geräte-Manager: Intel Arc 140T → „Das Gerät funktioniert einwandfrei.“
