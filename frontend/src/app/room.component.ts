import {Component, Input, OnInit} from '@angular/core';
import {Room} from './room';
import {HttpClient, HttpHeaders} from '@angular/common/http';

@Component({
  selector: 'app-room',
  templateUrl: './room.component.html',
  styleUrls: ['./room.component.css']
})
export class RoomComponent implements OnInit {
  private backendUrl = 'https://loosdorf.ddns.rueckgr.at/max/rooms/';

  @Input() room: Room;
  temperature: number;

  constructor(
    private http: HttpClient
  ) { }

  ngOnInit(): void {
    this.temperature = this.room.temperature;
  }

  update_room(room_id: number) {
    const url = this.backendUrl + room_id;

    const httpOptions = {
      headers: new HttpHeaders({ 'Content-Type': 'application/json' })
    };
    const body = {temperature: this.temperature};
    this.http.post(url, body, httpOptions).subscribe();
  }
}
