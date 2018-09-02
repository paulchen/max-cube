import {Component, OnInit} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Room} from './room';
import {RoomList} from './roomList';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  private backendUrl = 'https://loosdorf.ddns.rueckgr.at/max/rooms';
  private triggerUpdateUrl = 'https://loosdorf.ddns.rueckgr.at/max/update';

  rooms: Room[];

  constructor(
    private http: HttpClient
  ) { }

  ngOnInit() {
    this.reloadData();
  }

  reloadData() {
    this.http.get<RoomList>(this.backendUrl)
      .subscribe(rooms => {
        for (const room of rooms.rooms) {
          for (const device of room.devices) {
            room.temperature = device.temperature;
          }
        }
        this.rooms = rooms.rooms;
      });
  }

  triggerBackendUpdate() {
    this.http.get(this.triggerUpdateUrl).subscribe();
  }
}
