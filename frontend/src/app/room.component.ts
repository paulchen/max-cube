import {Component, Input, Output, OnInit, EventEmitter} from '@angular/core';
import {Room} from './room';

@Component({
  selector: 'app-room',
  templateUrl: './room.component.html',
  styleUrls: ['./room.component.css']
})
export class RoomComponent implements OnInit {
  private minTemperature = 5;
  private maxTemperature = 25;
  private step = .5;

  @Input() room: Room;
  @Output() roomChange = new EventEmitter();

  initialTemperature: number;
  temperature: number;
  decreaseDisabled: boolean = false;
  increaseDisabled: boolean = false;

  ngOnInit(): void {
    this.temperature = this.room.temperature;
    this.initialTemperature = this.temperature;

    this.updateButtons();
  }

  decreaseTemperature() {
    this.temperature = Math.max(this.temperature - this.step, this.minTemperature);
    this.handleChange();
  }

  increaseTemperature() {
    this.temperature = Math.min(this.temperature + this.step, this.maxTemperature);
    this.handleChange();
  }

  handleChange() {
    this.updateButtons();
    this.roomChange.emit({room: this.room, temperature: this.temperature});
  }

  updateButtons() {
    this.decreaseDisabled = this.temperature <= this.minTemperature;
    this.increaseDisabled = this.temperature >= this.maxTemperature;
  }
}
