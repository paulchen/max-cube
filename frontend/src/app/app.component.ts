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
  rooms: Room[];

  constructor(
    private http: HttpClient
  ) { }

  ngOnInit() {
    this.http.get<RoomList>(this.backendUrl)
      .subscribe(rooms => this.rooms = rooms.rooms);
  }
}
