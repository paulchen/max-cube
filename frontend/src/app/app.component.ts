import {Component, OnInit} from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {Room} from './room';
import {RoomList} from './roomList';
import {timer, forkJoin, of} from 'rxjs';
import {catchError} from 'rxjs/operators';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  private backendUrl = 'https://loosdorf.ddns.rueckgr.at/max/rooms';
  private triggerUpdateUrl = 'https://loosdorf.ddns.rueckgr.at/max/update';

  private waitTime1 = 60000;
  private waitTime2 = 15000;

  rooms: Room[];
  newTemperatures: {[ roomId: number]: number } = [];

  saveDisabled: boolean = true;
  showSpinner: boolean = true;
  showContent: boolean = false;

  msgs = [];

  constructor(
    private http: HttpClient
  ) { }

  ngOnInit() {
    this.reloadData().subscribe(rooms => {
      this.reloadRooms(rooms);

      this.showSpinner = false;
      this.showContent = true;
    });
  }

  reloadRooms(rooms) {
    for (const room of rooms.rooms) {
      for (const device of room.devices) {
        room.temperature = device.temperature;
      }
    }
    this.rooms = rooms.rooms;
  }

  reloadData() {
    return this.http.get<RoomList>(this.backendUrl);
  }

  triggerBackendUpdate() {
    return this.http.get(this.triggerUpdateUrl);
  }

  roomChange(event) {
    this.newTemperatures[event.room.id] = event.temperature;
    this.saveDisabled = this.findChangedRooms().length == 0;
  }

  findChangedRooms() {
    return this.rooms.filter(room => room.id in this.newTemperatures && room.temperature != this.newTemperatures[room.id]);
  }

  updateRooms() {
    this.showSpinner = true;
    this.showContent = false;

    this.msgs = [];
    this.msgs.push({severity: 'info', summary: 'Hinweis', detail: 'Bitte warten, während die Änderungen gespeichert werden.'});

    const observables = [];
    for (const room of this.findChangedRooms()) {
      const observable = this.updateRoom(room.id)
        .pipe(catchError(() => {
          return of(undefined)
        }));
      observables.push(observable);
    }

    forkJoin(observables).subscribe(results => {
      if(results.includes(undefined)) {
        this.showError();
        return;
      }

      timer(this.waitTime1).subscribe(val => {
        this.triggerBackendUpdate().subscribe(() => {
          timer(this.waitTime2).subscribe(val => {
            this.reloadData().subscribe(rooms => {
              this.reloadRooms(rooms);
              this.showSuccess();
            },
            error => {
              this.showError();
            });
           },
           error => {
             this.showError();
           });
        });
      });
    });
  }

  showSuccess() {
    this.showSpinner = false;
    this.showContent = true;

    this.msgs = [];
    this.msgs.push({severity: 'success', summary: 'Gespeichert', detail: 'Die Änderungen wurden erfolgreich gespeichert.'});

    this.saveDisabled = true;
  }

  showError() {
    this.showSpinner = false;

    this.msgs = [];
    this.msgs.push({severity: 'error', summary: 'Fehler', detail: 'Beim Speichern der Änderungen ist ein Fehler aufgetreten.'});
  }

  updateRoom(room_id: number) {
    const newTemperature = this.newTemperatures[room_id];
    console.log('Changing room ' + room_id + ' to ' + newTemperature);

    const url = this.backendUrl + '/' + room_id;

    const httpOptions = {
      headers: new HttpHeaders({ 'Content-Type': 'application/json' })
    };
    const body = {temperature: newTemperature};
    return this.http.post(url, body, httpOptions);
  }
}
