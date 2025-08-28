import { Component, ElementRef, Input, OnInit, ViewChild, ViewEncapsulation } from '@angular/core';
import { Observable } from 'rxjs';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';
import { filter, map } from 'rxjs/operators';
import { DataUtilities } from '../../utilities/data.utilities';
import {ApiContentElement, ApiHint} from '../../../../openapi';

@Component({
  selector: 'app-video-object-preview',
  template: `
    <div class="video-container">
      <video
        #player
        *ngIf="videoUrl | async"
        [src]="videoUrl | async"
        class="video-player"
        controls
        [muted]="muted"
        (canplay)="handleCanPlay()"
        (ended)="handleEnded()"
        (fullscreen)="handleFullscreen()"
      ></video>
    </div>
  `,
  styleUrls: ['./video-object-preview.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class VideoObjectPreviewComponent implements OnInit {
  /** Observable of current {@link ContentElement} that should be displayed. Provided by user of this component. */
  @Input() queryObject: Observable<ApiContentElement>;

  /** Flag indicating whether video player should be muted or not. Can be provided by a user of this component. */
  @Input() muted = true;

  /** Indicates after how many repetitions the video player should be muted (default = 1). Can be provided by a user of this component. */
  @Input() muteAfter = 1;

  /** Reference to the {@link HTMLVideoElement} used for playback. */
  @ViewChild('player') player: ElementRef<HTMLVideoElement>;

  /** Current video to display (as data URL). */
  videoUrl: Observable<SafeUrl>;
  numberOfLoops = 0;

  constructor(private sanitizer: DomSanitizer) {}

  ngOnInit(): void {
    this.videoUrl = this.queryObject.pipe(
      filter((q) => q.contentType === 'VIDEO'),
      map((q) => {
        if (q.content) {
          return this.sanitizer.bypassSecurityTrustUrl(DataUtilities.base64ToUrl(q.content, 'video/mp4'));
        } else {
          return null;
        }
      })
    );
  }

  /**
   * Handles availability of data for video player. Requests fullscreen mode and starts playback
   */
  public handleCanPlay() {
    this.player.nativeElement.play().then((s) => {});
  }

  /**
   * Handles entering fullscreen mode in video player.
   */
  public handleFullscreen() {
    this.player.nativeElement.requestFullscreen().then((s) => {});
  }

  /**
   * Handles end of playback in video player. Mutes video and exists fullscreen mode (if enabled). Then restarts playback.
   */
  public handleEnded() {
    this.player.nativeElement.play().then((s) => {
      this.numberOfLoops += 1;
      this.muted = this.numberOfLoops >= this.muteAfter;
    });
  }
}
