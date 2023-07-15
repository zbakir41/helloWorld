import snap7.client as c
import snap7.util as u
from flask import Flask, render_template, request, session, redirect, url_for,flash
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Session anahtarını ayarlayın

from snap7.types import Areas
plc_ip='140.80.80.80'
def oku_plc(Byte,bit):
        reading=plc.read_area(Areas.DB,1,Byte,1)
        rt=u.get_bool(reading,0,bit)
        return rt
class AkilliEv:
    def __init__(self):
        self.salon_isik = False
        self.mutfak_isik = False
        self.yatak_odasi_isik = False
        self.kapi_kilit = True
        self.klima_durumu = False
        self.plc = c.Client()
        self.plc.connect('140.80.80.80', 0, 1)  # PLC IP adresi ve bağlantı parametrelerini ayarlayın

    def update_plc(self):
        self.plc.write_area(Areas.DB, 1, 0, bytearray([int(self.salon_isik)]))
        self.plc.write_area(Areas.DB, 1, 1, bytearray([int(self.mutfak_isik)]))
        self.plc.write_area(Areas.DB, 1, 2, bytearray([int(self.yatak_odasi_isik)]))
        self.plc.write_area(Areas.DB, 1, 3, bytearray([int(self.kapi_kilit)]))
        self.plc.write_area(Areas.DB, 1, 4, bytearray([int(self.klima_durumu)]))

    def salon_isik_ac(self):
        self.salon_isik = True
        print("Salon ışığı açıldı.")

    def salon_isik_kapat(self):
        self.salon_isik = False
        print("Salon ışığı kapatıldı.")

    def mutfak_isik_ac(self):
        self.mutfak_isik = True
        print("Mutfak ışığı açıldı.")

    def mutfak_isik_kapat(self):
        self.mutfak_isik = False
        print("Mutfak ışığı kapatıldı.")

    def yatak_odasi_isik_ac(self):
        self.yatak_odasi_isik = True
        print("Yatak odası ışığı açıldı.")

    def yatak_odasi_isik_kapat(self):
        self.yatak_odasi_isik = False
        print("Yatak odası ışığı kapatıldı.")

    def kapi_kilit_ac(self):
        self.kapi_kilit = True
        print("Kapı kilitlendi.")

    def kapi_kilit_kapat(self):
        self.kapi_kilit = False
        print("Kapı açıldı.")

    def klima_ac(self):
        self.klima_durumu = True
        print("Klima açıldı.")

    def klima_kapat(self):
        self.klima_durumu = False
        print("Klima kapatıldı.")

    def get_salon_isik_durumu(self):
        data = bytearray(1)
        self.plc.db_read(1, 0, data)
        return bool(data[0])

    def get_mutfak_isik_durumu(self):
        data = bytearray(1)
        self.plc.db_read(1, 1, data)
        return bool(data[0])

    def get_yatak_odasi_isik_durumu(self):
        data = bytearray(1)
        self.plc.db_read(1, 2, data)
        return bool(data[0])

    def get_kapi_kilit_durumu(self):
        data = bytearray(1)
        self.plc.db_read(1, 3, data)
        return bool(data[0])

    def get_klima_durumu(self):
        data = bytearray(1)
        self.plc.db_read(1, 4, data)
        return bool(data[0])

akilli_ev = AkilliEv()

@app.route('/', methods=['GET', 'POST'])
def index():
    if not akilli_ev.plc.get_connected():
        akilli_ev.plc.connect(plc_ip, 0, 1)
        flash('PLC bağlantısı kuruldu.', 'success') 
    if request.method == 'POST':
        if 'salon_isik' in request.form:
            if akilli_ev.salon_isik:
                akilli_ev.salon_isik_kapat()
            else:
                akilli_ev.salon_isik_ac()
        elif 'mutfak_isik' in request.form:
            if akilli_ev.mutfak_isik:
                akilli_ev.mutfak_isik_kapat()
            else:
                akilli_ev.mutfak_isik_ac()
        elif 'yatak_odasi_isik' in request.form:
            if akilli_ev.yatak_odasi_isik:
                akilli_ev.yatak_odasi_isik_kapat()
            else:
                akilli_ev.yatak_odasi_isik_ac()
        elif 'kapi_kilit' in request.form:
            if akilli_ev.kapi_kilit:
                akilli_ev.kapi_kilit_kapat()
            else:
                akilli_ev.kapi_kilit_ac()
        elif 'klima_durumu' in request.form:
            if akilli_ev.klima_durumu:
                akilli_ev.klima_kapat()
            else:
                akilli_ev.klima_ac()
        try:
            akilli_ev.update_plc()  # PLC'ye güncel durumu gönder
        except Exception as e:
            return render_template('index.html', akilli_ev=akilli_ev, error_message=str(e))
            

        return redirect(url_for('index'))  # Sayfayı yeniden yönlendir
    else:
        # Buton durumlarını PLC'den al
        try:
            data=akilli_ev.plc.read_area(Areas.DB, 1, 0,16)
            akilli_ev.salon_isik = u.get_bool(data,0,0)
            akilli_ev.mutfak_isik = u.get_bool(data,1,0)
            akilli_ev.yatak_odasi_isik = u.get_bool(data,2,0)
            akilli_ev.kapi_kilit = u.get_bool(data,3,0)
            akilli_ev.klima_durumu = u.get_bool(data,4,0)

        except :
            time.sleep(5)
            return redirect(url_for('index'))  # Sayfayı yeniden yönlendir
            
        
        
        # Buton durumlarını session üzerine kaydet
        session['salon_isik'] = akilli_ev.salon_isik
        session['mutfak_isik'] = akilli_ev.mutfak_isik
        session['yatak_odasi_isik'] = akilli_ev.yatak_odasi_isik
        session['kapi_kilit'] = akilli_ev.kapi_kilit
        session['klima_durumu'] = akilli_ev.klima_durumu

    return render_template('index.html', akilli_ev=akilli_ev)

if __name__ == '__main__':
    app.run(debug=True)