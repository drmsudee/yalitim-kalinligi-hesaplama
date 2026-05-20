import tkinter as tk
from tkinter import messagebox
import math

def toplam_direnc_tek_katman(
    boru_ic_yaricap,
    boru_dis_yaricap,
    yalitim_dis_yaricap,
    ic_tasinim_katsayisi,
    dis_tasinim_katsayisi,
    boru_isi_iletkenligi,
    yalitim1_isi_iletkenligi,
    boru_uzunlugu
):
    return (
        1 / (ic_tasinim_katsayisi * 2 * math.pi * boru_ic_yaricap * boru_uzunlugu)
        + math.log(boru_dis_yaricap / boru_ic_yaricap) / (2 * math.pi * boru_isi_iletkenligi * boru_uzunlugu)
        + math.log(yalitim_dis_yaricap / boru_dis_yaricap) / (2 * math.pi * yalitim1_isi_iletkenligi * boru_uzunlugu)
        + 1 / (dis_tasinim_katsayisi * 2 * math.pi * yalitim_dis_yaricap * boru_uzunlugu)
    )


def toplam_direnc_iki_katman(
    boru_ic_yaricap,
    boru_dis_yaricap,
    birinci_katman_dis_yaricap,
    ikinci_katman_dis_yaricap,
    ic_tasinim_katsayisi,
    dis_tasinim_katsayisi,
    boru_isi_iletkenligi,
    yalitim1_isi_iletkenligi,
    yalitim2_isi_iletkenligi,
    boru_uzunlugu
):
    return (
        1 / (ic_tasinim_katsayisi * 2 * math.pi * boru_ic_yaricap * boru_uzunlugu)
        + math.log(boru_dis_yaricap / boru_ic_yaricap) / (2 * math.pi * boru_isi_iletkenligi * boru_uzunlugu)
        + math.log(birinci_katman_dis_yaricap / boru_dis_yaricap) / (2 * math.pi * yalitim1_isi_iletkenligi * boru_uzunlugu)
        + math.log(ikinci_katman_dis_yaricap / birinci_katman_dis_yaricap) / (2 * math.pi * yalitim2_isi_iletkenligi * boru_uzunlugu)
        + 1 / (dis_tasinim_katsayisi * 2 * math.pi * ikinci_katman_dis_yaricap * boru_uzunlugu)
    )


def isi_kaybi(ic_sicaklik, dis_sicaklik, toplam_direnc):
    return (ic_sicaklik - dis_sicaklik) / toplam_direnc  # W


def yillik_enerji_maliyeti(isi_kaybi_watt, yillik_calisma_suresi_saat, enerji_birim_fiyati):
    return (isi_kaybi_watt * yillik_calisma_suresi_saat / 1000.0) * enerji_birim_fiyati  # TL/yıl


def tek_katman_yatirim_maliyeti(boru_dis_yaricap, yalitim_dis_yaricap, boru_uzunlugu, birinci_katman_maliyet):
    hacim = math.pi * (yalitim_dis_yaricap ** 2 - boru_dis_yaricap ** 2) * boru_uzunlugu
    return hacim * birinci_katman_maliyet


def iki_katman_yatirim_maliyeti(
    boru_dis_yaricap,
    birinci_katman_dis_yaricap,
    ikinci_katman_dis_yaricap,
    boru_uzunlugu,
    birinci_katman_maliyet,
    ikinci_katman_maliyet
):
    birinci_hacim = math.pi * (birinci_katman_dis_yaricap ** 2 - boru_dis_yaricap ** 2) * boru_uzunlugu
    ikinci_hacim = math.pi * (ikinci_katman_dis_yaricap ** 2 - birinci_katman_dis_yaricap ** 2) * boru_uzunlugu
    return birinci_hacim * birinci_katman_maliyet + ikinci_hacim * ikinci_katman_maliyet


def optimum_tek_katman(parametreler):
    en_iyi_sonuc = None
    adim = 0.001  # 1 mm (kod içinde sabit)
    kalinlik = 0.0

    while kalinlik <= 0.30:  # 30 cm'e kadar iç arama
        yalitim_dis_yaricap = parametreler["boru_dis_yaricap"] + kalinlik

        direnç = toplam_direnc_tek_katman(
            parametreler["boru_ic_yaricap"],
            parametreler["boru_dis_yaricap"],
            yalitim_dis_yaricap,
            parametreler["ic_tasinim_katsayisi"],
            parametreler["dis_tasinim_katsayisi"],
            parametreler["boru_isi_iletkenligi"],
            parametreler["birinci_katman_isi_iletkenligi"],
            parametreler["boru_uzunlugu"]
        )

        q = isi_kaybi(parametreler["ic_sicaklik"], parametreler["dis_sicaklik"], direnç)
        yillik_maliyet = yillik_enerji_maliyeti(q, parametreler["yillik_calisma_suresi"], parametreler["enerji_fiyati"])
        yatirim = tek_katman_yatirim_maliyeti(
            parametreler["boru_dis_yaricap"],
            yalitim_dis_yaricap,
            parametreler["boru_uzunlugu"],
            parametreler["birinci_katman_maliyeti"]
        )

        toplam = yillik_maliyet + yatirim

        if en_iyi_sonuc is None or toplam < en_iyi_sonuc["toplam_maliyet"]:
            en_iyi_sonuc = {
                "birinci_katman_kalinligi": kalinlik,
                "isi_kaybi": q,
                "yillik_maliyet": yillik_maliyet,
                "yatirim_maliyeti": yatirim,
                "toplam_maliyet": toplam
            }

        kalinlik += adim

    return en_iyi_sonuc


def optimum_iki_katman(parametreler):
    en_iyi_sonuc = None
    adim = 0.001  # 1 mm (kod içinde sabit)

    birinci_kalinlik = 0.0
    while birinci_kalinlik <= 0.20:  # 20 cm
        birinci_katman_dis_yaricap = parametreler["boru_dis_yaricap"] + birinci_kalinlik

        ikinci_kalinlik = 0.0
        while ikinci_kalinlik <= 0.20:  # 20 cm
            ikinci_katman_dis_yaricap = birinci_katman_dis_yaricap + ikinci_kalinlik

            direnç = toplam_direnc_iki_katman(
                parametreler["boru_ic_yaricap"],
                parametreler["boru_dis_yaricap"],
                birinci_katman_dis_yaricap,
                ikinci_katman_dis_yaricap,
                parametreler["ic_tasinim_katsayisi"],
                parametreler["dis_tasinim_katsayisi"],
                parametreler["boru_isi_iletkenligi"],
                parametreler["birinci_katman_isi_iletkenligi"],
                parametreler["ikinci_katman_isi_iletkenligi"],
                parametreler["boru_uzunlugu"]
            )

            q = isi_kaybi(parametreler["ic_sicaklik"], parametreler["dis_sicaklik"], direnç)
            yillik_maliyet = yillik_enerji_maliyeti(q, parametreler["yillik_calisma_suresi"], parametreler["enerji_fiyati"])
            yatirim = iki_katman_yatirim_maliyeti(
                parametreler["boru_dis_yaricap"],
                birinci_katman_dis_yaricap,
                ikinci_katman_dis_yaricap,
                parametreler["boru_uzunlugu"],
                parametreler["birinci_katman_maliyeti"],
                parametreler["ikinci_katman_maliyeti"]
            )

            toplam = yillik_maliyet + yatirim

            if en_iyi_sonuc is None or toplam < en_iyi_sonuc["toplam_maliyet"]:
                en_iyi_sonuc = {
                    "birinci_katman_kalinligi": birinci_kalinlik,
                    "ikinci_katman_kalinligi": ikinci_kalinlik,
                    "isi_kaybi": q,
                    "yillik_maliyet": yillik_maliyet,
                    "yatirim_maliyeti": yatirim,
                    "toplam_maliyet": toplam
                }

            ikinci_kalinlik += adim

        birinci_kalinlik += adim

    return en_iyi_sonuc


class YalitimProgrami:
    def __init__(self, root):
        self.root = root
        self.root.title("Optimum Yalıtım Kalınlığı Hesaplama Programı")
        self.root.geometry("1100x700")
        self.root.configure(bg="#f4f6f8")

        self.girdiler = {}
        self.ikinci_katman_kullan = tk.BooleanVar(value=False)

        self.arayuz_olustur()

    def giris_ekle(self, ebeveyn, metin, anahtar, satir):
        etiket = tk.Label(
            ebeveyn,
            text=metin,
            font=("Arial", 11),
            bg="#f4f6f8",
            anchor="w",
            justify="left"
        )
        etiket.grid(row=satir, column=0, sticky="w", padx=5, pady=8)

        kutu = tk.Entry(ebeveyn, width=22, font=("Arial", 11))
        kutu.grid(row=satir, column=1, padx=5, pady=8)

        self.girdiler[anahtar] = kutu

    def arayuz_olustur(self):
        baslik = tk.Label(
            self.root,
            text="Optimum Yalıtım Kalınlığı Hesaplama Programı",
            font=("Arial", 16, "bold"),
            bg="#f4f6f8",
            fg="#1f2d3d"
        )
        baslik.pack(pady=15)

        ana_cerceve = tk.Frame(self.root, bg="#f4f6f8")
        ana_cerceve.pack(pady=10)

        sol_cerceve = tk.LabelFrame(
            ana_cerceve,
            text="Boru ve Çevre Bilgileri",
            font=("Arial", 12, "bold"),
            bg="#f4f6f8",
            padx=15,
            pady=10
        )
        sol_cerceve.grid(row=0, column=0, padx=20, sticky="n")

        sag_cerceve = tk.LabelFrame(
            ana_cerceve,
            text="Yalıtım ve Maliyet Bilgileri",
            font=("Arial", 12, "bold"),
            bg="#f4f6f8",
            padx=15,
            pady=10
        )
        sag_cerceve.grid(row=0, column=1, padx=20, sticky="n")

        self.giris_ekle(sol_cerceve, "Boru iç çapı (mm):", "boru_ic_cap", 0)
        self.giris_ekle(sol_cerceve, "Boru dış çapı (mm):", "boru_dis_cap", 1)
        self.giris_ekle(sol_cerceve, "Boru uzunluğu (m):", "boru_uzunlugu", 2)
        self.giris_ekle(sol_cerceve, "İç akışkan sıcaklığı (°C):", "ic_sicaklik", 3)
        self.giris_ekle(sol_cerceve, "Dış ortam sıcaklığı (°C):", "dis_sicaklik", 4)
        self.giris_ekle(sol_cerceve, "İç yüzey taşınım katsayısı (W/m²K):", "ic_tasinim_katsayisi", 5)
        self.giris_ekle(sol_cerceve, "Dış yüzey taşınım katsayısı (W/m²K):", "dis_tasinim_katsayisi", 6)
        self.giris_ekle(sol_cerceve, "Boru malzemesi ısı iletkenliği (W/mK):", "boru_isi_iletkenligi", 7)

        self.giris_ekle(sag_cerceve, "1. katman ısı iletkenliği (W/mK):", "birinci_katman_isi_iletkenligi", 0)
        self.giris_ekle(sag_cerceve, "1. katman birim maliyeti (TL/m³):", "birinci_katman_maliyeti", 1)

        ikinci_katman_kutusu = tk.Checkbutton(
            sag_cerceve,
            text="Opsiyonel 2. katman kullan",
            variable=self.ikinci_katman_kullan,
            command=self.ikinci_katman_durumu_guncelle,
            font=("Arial", 11),
            bg="#f4f6f8"
        )
        ikinci_katman_kutusu.grid(row=2, column=0, columnspan=2, sticky="w", pady=10)

        self.giris_ekle(sag_cerceve, "2. katman ısı iletkenliği (W/mK):", "ikinci_katman_isi_iletkenligi", 3)
        self.giris_ekle(sag_cerceve, "2. katman birim maliyeti (TL/m³):", "ikinci_katman_maliyeti", 4)
        self.giris_ekle(sag_cerceve, "Enerji birim fiyatı (TL/kWh):", "enerji_fiyati", 5)
        self.giris_ekle(sag_cerceve, "Yıllık çalışma süresi (saat/yıl):", "yillik_calisma_suresi", 6)

        buton_cercevesi = tk.Frame(self.root, bg="#f4f6f8")
        buton_cercevesi.pack(pady=15)

        hesapla_butonu = tk.Button(
            buton_cercevesi,
            text="HESAPLA",
            width=18,
            height=2,
            font=("Arial", 11, "bold"),
            bg="#2e86de",
            fg="white",
            command=self.hesapla
        )
        hesapla_butonu.grid(row=0, column=0, padx=12)

        temizle_butonu = tk.Button(
            buton_cercevesi,
            text="TEMİZLE",
            width=18,
            height=2,
            font=("Arial", 11, "bold"),
            bg="#95a5a6",
            fg="white",
            command=self.temizle
        )
        temizle_butonu.grid(row=0, column=1, padx=12)

        self.sonuc_alani = tk.Text(
            self.root,
            width=110,
            height=15,
            font=("Consolas", 11),
            bd=2,
            relief="groove"
        )
        self.sonuc_alani.pack(padx=20, pady=10)

        self.ikinci_katman_durumu_guncelle()

    def ikinci_katman_durumu_guncelle(self):
        durum = "normal" if self.ikinci_katman_kullan.get() else "disabled"
        self.girdiler["ikinci_katman_isi_iletkenligi"].config(state=durum)
        self.girdiler["ikinci_katman_maliyeti"].config(state=durum)

    def sayi_al(self, anahtar, alan_adi):
        deger = self.girdiler[anahtar].get().strip()
        if deger == "":
            raise ValueError(f"{alan_adi} boş bırakılamaz.")
        return float(deger)

    def temizle(self):
        for kutu in self.girdiler.values():
            kutu.config(state="normal")
            kutu.delete(0, tk.END)

        self.ikinci_katman_kullan.set(False)
        self.ikinci_katman_durumu_guncelle()
        self.sonuc_alani.delete("1.0", tk.END)

    def hesapla(self):
        try:
            boru_ic_cap_mm = self.sayi_al("boru_ic_cap", "Boru iç çapı")
            boru_dis_cap_mm = self.sayi_al("boru_dis_cap", "Boru dış çapı")
            boru_uzunlugu = self.sayi_al("boru_uzunlugu", "Boru uzunluğu")
            ic_sicaklik = self.sayi_al("ic_sicaklik", "İç akışkan sıcaklığı")
            dis_sicaklik = self.sayi_al("dis_sicaklik", "Dış ortam sıcaklığı")
            ic_tasinim_katsayisi = self.sayi_al("ic_tasinim_katsayisi", "İç yüzey taşınım katsayısı")
            dis_tasinim_katsayisi = self.sayi_al("dis_tasinim_katsayisi", "Dış yüzey taşınım katsayısı")
            boru_isi_iletkenligi = self.sayi_al("boru_isi_iletkenligi", "Boru malzemesi ısı iletkenliği")
            birinci_katman_isi_iletkenligi = self.sayi_al("birinci_katman_isi_iletkenligi", "1. katman ısı iletkenliği")
            birinci_katman_maliyeti = self.sayi_al("birinci_katman_maliyeti", "1. katman birim maliyeti")
            enerji_fiyati = self.sayi_al("enerji_fiyati", "Enerji birim fiyatı")
            yillik_calisma_suresi = self.sayi_al("yillik_calisma_suresi", "Yıllık çalışma süresi")

            if boru_ic_cap_mm <= 0 or boru_dis_cap_mm <= 0 or boru_uzunlugu <= 0:
                raise ValueError("Çap ve uzunluk değerleri sıfırdan büyük olmalıdır.")

            if boru_dis_cap_mm <= boru_ic_cap_mm:
                raise ValueError("Boru dış çapı, boru iç çapından büyük olmalıdır.")

            if (
                ic_tasinim_katsayisi <= 0
                or dis_tasinim_katsayisi <= 0
                or boru_isi_iletkenligi <= 0
                or birinci_katman_isi_iletkenligi <= 0
            ):
                raise ValueError("Isı iletim ve taşınım katsayıları sıfırdan büyük olmalıdır.")

            if birinci_katman_maliyeti < 0 or enerji_fiyati < 0:
                raise ValueError("Maliyet değerleri negatif olamaz.")

            if yillik_calisma_suresi <= 0:
                raise ValueError("Yıllık çalışma süresi sıfırdan büyük olmalıdır.")

            parametreler = {
                "boru_ic_yaricap": boru_ic_cap_mm / 2000.0,
                "boru_dis_yaricap": boru_dis_cap_mm / 2000.0,
                "boru_uzunlugu": boru_uzunlugu,
                "ic_sicaklik": ic_sicaklik,
                "dis_sicaklik": dis_sicaklik,
                "ic_tasinim_katsayisi": ic_tasinim_katsayisi,
                "dis_tasinim_katsayisi": dis_tasinim_katsayisi,
                "boru_isi_iletkenligi": boru_isi_iletkenligi,
                "birinci_katman_isi_iletkenligi": birinci_katman_isi_iletkenligi,
                "birinci_katman_maliyeti": birinci_katman_maliyeti,
                "enerji_fiyati": enerji_fiyati,
                "yillik_calisma_suresi": yillik_calisma_suresi
            }

            self.sonuc_alani.delete("1.0", tk.END)

            if not self.ikinci_katman_kullan.get():
                sonuc = optimum_tek_katman(parametreler)

                self.sonuc_alani.insert(tk.END, "=== TEK KATMAN SONUÇLARI ===\n\n")
                self.sonuc_alani.insert(tk.END, f"Optimum 1. katman kalınlığı : {sonuc['birinci_katman_kalinligi'] * 100:.2f} cm\n")
                self.sonuc_alani.insert(tk.END, f"Isı kaybı                   : {sonuc['isi_kaybi']:.2f} W\n")
                self.sonuc_alani.insert(tk.END, f"Yıllık enerji maliyeti      : {sonuc['yillik_maliyet']:.2f} TL/yıl\n")
                self.sonuc_alani.insert(tk.END, f"Yalıtım yatırım maliyeti    : {sonuc['yatirim_maliyeti']:.2f} TL\n")
                self.sonuc_alani.insert(tk.END, f"Toplam maliyet              : {sonuc['toplam_maliyet']:.2f} TL\n")

            else:
                ikinci_katman_isi_iletkenligi = self.sayi_al("ikinci_katman_isi_iletkenligi", "2. katman ısı iletkenliği")
                ikinci_katman_maliyeti = self.sayi_al("ikinci_katman_maliyeti", "2. katman birim maliyeti")

                if ikinci_katman_isi_iletkenligi <= 0:
                    raise ValueError("2. katman ısı iletkenliği sıfırdan büyük olmalıdır.")
                if ikinci_katman_maliyeti < 0:
                    raise ValueError("2. katman birim maliyeti negatif olamaz.")

                parametreler["ikinci_katman_isi_iletkenligi"] = ikinci_katman_isi_iletkenligi
                parametreler["ikinci_katman_maliyeti"] = ikinci_katman_maliyeti

                sonuc = optimum_iki_katman(parametreler)

                self.sonuc_alani.insert(tk.END, "=== İKİ KATMAN SONUÇLARI ===\n\n")
                self.sonuc_alani.insert(tk.END, f"Optimum 1. katman kalınlığı : {sonuc['birinci_katman_kalinligi'] * 100:.2f} cm\n")
                self.sonuc_alani.insert(tk.END, f"Optimum 2. katman kalınlığı : {sonuc['ikinci_katman_kalinligi'] * 100:.2f} cm\n")
                self.sonuc_alani.insert(tk.END, f"Toplam yalıtım kalınlığı    : {(sonuc['birinci_katman_kalinligi'] + sonuc['ikinci_katman_kalinligi']) * 100:.2f} cm\n")
                self.sonuc_alani.insert(tk.END, f"Isı kaybı                   : {sonuc['isi_kaybi']:.2f} W\n")
                self.sonuc_alani.insert(tk.END, f"Yıllık enerji maliyeti      : {sonuc['yillik_maliyet']:.2f} TL/yıl\n")
                self.sonuc_alani.insert(tk.END, f"Yalıtım yatırım maliyeti    : {sonuc['yatirim_maliyeti']:.2f} TL\n")
                self.sonuc_alani.insert(tk.END, f"Toplam maliyet              : {sonuc['toplam_maliyet']:.2f} TL\n")

        except Exception as hata:
            messagebox.showerror("Hata", str(hata))


if __name__ == "__main__":
    pencere = tk.Tk()
    uygulama = YalitimProgrami(pencere)
    pencere.mainloop()