"""
Système de Notifications Avancé avec Son et Animations
"""

import customtkinter as ctk
from typing import Callable, Optional
import threading
from datetime import datetime
import queue

class NotificationManager:
    """
    Gestionnaire de notifications avec son et animations
    
    Attributes:
        parent: Fenêtre parent
        notification_queue: Queue des notifications
        colors (dict): Couleurs de l'application
    """
    
    SOUNDS = {
        'success': (800, 150),  # (fréquence, durée)
        'warning': (600, 200),
        'error': (400, 300),
        'info': (1000, 100)
    }
    
    def __init__(self, parent, colors: dict):
        """
        Initialise le gestionnaire de notifications
        
        Args:
            parent: Fenêtre parent
            colors (dict): Dictionnaire des couleurs
        """
        self.parent = parent
        self.colors = colors
        self.notification_queue = queue.Queue()
        self.active_notifications = []
        self.notification_enabled = False
        
        # Démarrer le worker de notifications
     
    
    def show(self, message: str, notif_type: str = 'info', 
            duration: int = 3000, sound: bool = True, 
            action: Optional[Callable] = None, action_text: str = "Action"):
        """
        Affiche une notification
        
        Args:
            message (str): Message à afficher
            notif_type (str): Type (success, warning, error, info)
            duration (int): Durée d'affichage en ms
            sound (bool): Jouer un son
            action (Callable): Fonction callback pour action
            action_text (str): Texte du bouton d'action
        """
        if not self.notification_enabled:
            return
        
        notification = {
            'message': message,
            'type': notif_type,
            'duration': duration,
            'sound': sound,
            'action': action,
            'action_text': action_text,
            'timestamp': datetime.now()
        }
        
        self.notification_queue.put(notification)
    
    def _start_notification_worker(self):
        """Démarre le worker qui traite les notifications"""
        def worker():
            while True:
                try:
                    notification = self.notification_queue.get()
                    
                    # Jouer le son dans un thread séparé
                    if notification['sound']:
                        sound_thread = threading.Thread(
                            target=self._play_sound,
                            args=(notification['type'],)
                        )
                        sound_thread.daemon = True
                        sound_thread.start()
                    
                    # Afficher la notification dans le thread principal
                    self.parent.after(0, self._display_notification, notification)
                    
                except Exception as e:
                    print(f"❌ Erreur notification worker: {e}")
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def _play_sound(self, notif_type: str):
        """
        Joue un son de notification
        
        Args:
            notif_type (str): Type de notification
        """
        try:
            freq, duration = self.SOUNDS.get(notif_type, (1000, 100))
            winsound.Beep(freq, duration)
        except Exception as e:
            print(f"❌ Erreur son: {e}")
    
    def _display_notification(self, notification: dict):
        """
        Affiche une notification à l'écran
        
        Args:
            notification (dict): Données de la notification
        """
        # Nettoyage des vieilles notifications
        self._cleanup_old_notifications()
        
        # Couleurs selon le type
        type_colors = {
            'success': self.colors['success'],
            'warning': self.colors['warning'],
            'error': self.colors['danger'],
            'info': self.colors['primary']
        }
        
        type_icons = {
            'success': '✅',
            'warning': '⚠️',
            'error': '❌',
            'info': 'ℹ️'
        }
        
        bg_color = type_colors.get(notification['type'], self.colors['primary'])
        icon = type_icons.get(notification['type'], 'ℹ️')
        
        # Calculer la position (empilées en haut à droite)
        y_offset = 10 + (len(self.active_notifications) * 90)
        
        # Frame de notification
        notif_frame = ctk.CTkFrame(
            self.parent,
            fg_color=bg_color,
            corner_radius=10,
            width=350,
            height=80
        )
        
        # Positionner en haut à droite
        notif_frame.place(x=self.parent.winfo_width() - 370, y=y_offset)
        notif_frame.pack_propagate(False)
        
        # Container principal
        main_container = ctk.CTkFrame(notif_frame, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Header avec icon et bouton fermer
        header = ctk.CTkFrame(main_container, fg_color="transparent")
        header.pack(fill="x")
        
        # Icon
        ctk.CTkLabel(
            header,
            text=icon,
            font=ctk.CTkFont(size=24)
        ).pack(side="left", padx=(0, 10))
        
        # Bouton fermer
        close_btn = ctk.CTkButton(
            header,
            text="✕",
            width=25,
            height=25,
            fg_color="transparent",
            hover_color=self.colors['dark'],
            font=ctk.CTkFont(size=16),
            command=lambda: self._close_notification(notif_frame)
        )
        close_btn.pack(side="right")
        
        # Message
        message_label = ctk.CTkLabel(
            main_container,
            text=notification['message'],
            font=ctk.CTkFont(size=13),
            text_color="white",
            wraplength=280,
            justify="left"
        )
        message_label.pack(pady=(5, 5), anchor="w")
        
        # Bouton d'action si fourni
        if notification['action']:
            action_btn = ctk.CTkButton(
                main_container,
                text=notification['action_text'],
                width=100,
                height=25,
                fg_color="white",
                text_color=bg_color,
                hover_color=self.colors['light'],
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda: self._handle_action(
                    notification['action'], 
                    notif_frame
                )
            )
            action_btn.pack(pady=(5, 0), anchor="w")
        
        # Animation d'entrée
        self._animate_entrance(notif_frame)
        
        # Ajouter à la liste active
        self.active_notifications.append(notif_frame)
        
        # Auto-fermeture après durée
        if notification['duration'] > 0:
            self.parent.after(
                notification['duration'],
                lambda: self._close_notification(notif_frame)
            )
    
    def _animate_entrance(self, frame: ctk.CTkFrame):
        """
        Animation d'entrée de la notification
        
        Args:
            frame: Frame à animer
        """
        # Slide in de la droite
        target_x = self.parent.winfo_width() - 370
        current_x = self.parent.winfo_width()
        
        def slide():
            nonlocal current_x
            if current_x > target_x:
                current_x -= 20
                frame.place(x=current_x)
                self.parent.after(10, slide)
        
        slide()
    
    def _animate_exit(self, frame: ctk.CTkFrame, callback: Callable):
        """
        Animation de sortie de la notification
        
        Args:
            frame: Frame à animer
            callback: Fonction à appeler après l'animation
        """
        # Fade out
        current_x = frame.winfo_x()
        target_x = self.parent.winfo_width()
        
        def slide():
            nonlocal current_x
            if current_x < target_x:
                current_x += 20
                frame.place(x=current_x)
                self.parent.after(10, slide)
            else:
                callback()
        
        slide()
    
    def _close_notification(self, frame: ctk.CTkFrame):
        """
        Ferme une notification
        
        Args:
            frame: Frame à fermer
        """
        def remove():
            if frame in self.active_notifications:
                self.active_notifications.remove(frame)
                frame.destroy()
                self._reposition_notifications()
        
        self._animate_exit(frame, remove)
    
    def _handle_action(self, action: Callable, frame: ctk.CTkFrame):
        """
        Gère le clic sur le bouton d'action
        
        Args:
            action: Fonction callback
            frame: Frame de la notification
        """
        try:
            action()
        except Exception as e:
            print(f"❌ Erreur action notification: {e}")
        finally:
            self._close_notification(frame)
    
    def _reposition_notifications(self):
        """Repositionne toutes les notifications actives"""
        for i, notif in enumerate(self.active_notifications):
            y_offset = 10 + (i * 90)
            notif.place(y=y_offset)
    
    def _cleanup_old_notifications(self):
        """Nettoie les notifications expirées"""
        now = datetime.now()
        to_remove = []
        
        for notif in self.active_notifications:
            try:
                # Vérifier si le widget existe toujours
                if not notif.winfo_exists():
                    to_remove.append(notif)
            except:
                to_remove.append(notif)
        
        for notif in to_remove:
            if notif in self.active_notifications:
                self.active_notifications.remove(notif)
    
    def clear_all(self):
        """Ferme toutes les notifications"""
        for notif in self.active_notifications[:]:
            self._close_notification(notif)
    
    def enable(self):
        """Active les notifications"""
        self.notification_enabled = True
    
    def disable(self):
        """Désactive les notifications"""
        self.notification_enabled = False


class ToastNotification:
    """
    Notification Toast simple (sans queue)
    """
    
    @staticmethod
    def show(parent, message: str, duration: int = 2000, 
            bg_color: str = "#1976D2", text_color: str = "white"):
        """
        Affiche une notification toast simple
        
        Args:
            parent: Widget parent
            message (str): Message
            duration (int): Durée en ms
            bg_color (str): Couleur de fond
            text_color (str): Couleur du texte
        """
        # Frame toast
        toast = ctk.CTkFrame(
            parent,
            fg_color=bg_color,
            corner_radius=8,
            height=50
        )
        
        # Message
        label = ctk.CTkLabel(
            toast,
            text=message,
            font=ctk.CTkFont(size=13),
            text_color=text_color
        )
        label.pack(padx=20, pady=15)
        
        # Positionner en bas au centre
        toast.place(relx=0.5, rely=0.9, anchor="center")
        
        # Animation fade in
        toast.configure(fg_color=bg_color)
        
        # Auto-destruction
        def destroy_toast():
            toast.destroy()
        
        parent.after(duration, destroy_toast)


class AlertDialog:
    """
    Dialogue d'alerte personnalisé
    """
    
    @staticmethod
    def show_alert(parent, title: str, message: str, alert_type: str = 'warning',
                  on_confirm: Optional[Callable] = None, 
                  on_cancel: Optional[Callable] = None,
                  confirm_text: str = "OK", 
                  cancel_text: str = "Annuler"):
        """
        Affiche un dialogue d'alerte
        
        Args:
            parent: Fenêtre parent
            title (str): Titre
            message (str): Message
            alert_type (str): Type (warning, error, success, info)
            on_confirm: Callback confirmation
            on_cancel: Callback annulation
            confirm_text (str): Texte bouton confirmation
            cancel_text (str): Texte bouton annulation
        """
        dialog = ctk.CTkToplevel(parent)
        dialog.title(title)
        dialog.geometry("450x250")
        dialog.transient(parent)
        dialog.wait_visibility()
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Centrer
        dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (450 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (250 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Couleurs selon type
        colors = {
            'warning': '#FF9800',
            'error': '#F44336',
            'success': '#4CAF50',
            'info': '#1976D2'
        }
        
        icons = {
            'warning': '⚠️',
            'error': '❌',
            'success': '✅',
            'info': 'ℹ️'
        }
        
        color = colors.get(alert_type, '#1976D2')
        icon = icons.get(alert_type, 'ℹ️')
        
        # Header
        header = ctk.CTkFrame(dialog, fg_color=color, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text=icon,
            font=ctk.CTkFont(size=48)
        ).pack(pady=15)
        
        # Content
        content = ctk.CTkFrame(dialog, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=20)
        
        ctk.CTkLabel(
            content,
            text=message,
            font=ctk.CTkFont(size=14),
            wraplength=380,
            justify="center"
        ).pack(pady=20)
        
        # Buttons
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        def handle_confirm():
            dialog.destroy()
            if on_confirm:
                on_confirm()
        
        def handle_cancel():
            dialog.destroy()
            if on_cancel:
                on_cancel()
        
        ctk.CTkButton(
            btn_frame,
            text=confirm_text,
            command=handle_confirm,
            width=120,
            height=40,
            fg_color=color
        ).pack(side="left", padx=5)
        
        if on_cancel:
            ctk.CTkButton(
                btn_frame,
                text=cancel_text,
                command=handle_cancel,
                width=120,
                height=40,
                fg_color="gray"
            ).pack(side="left", padx=5)
        
        # Son
        try:
            if alert_type == 'error':
                winsound.Beep(400, 300)
            elif alert_type == 'warning':
                winsound.Beep(600, 200)
            elif alert_type == 'success':
                winsound.Beep(800, 150)
        except:
            pass


class ProgressDialog:
    """
    Dialogue de progression avec barre
    """
    
    def __init__(self, parent, title: str, message: str, max_value: int = 100):
        """
        Initialise le dialogue de progression
        
        Args:
            parent: Fenêtre parent
            title (str): Titre
            message (str): Message
            max_value (int): Valeur maximale
        """
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.wait_visibility()
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        # Centrer
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (400 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (200 // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self.max_value = max_value
        self.current_value = 0
        
        # Content
        content = ctk.CTkFrame(self.dialog, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Message
        self.message_label = ctk.CTkLabel(
            content,
            text=message,
            font=ctk.CTkFont(size=14)
        )
        self.message_label.pack(pady=20)
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(content, width=340)
        self.progress.pack(pady=10)
        self.progress.set(0)
        
        # Percentage
        self.percent_label = ctk.CTkLabel(
            content,
            text="0%",
            font=ctk.CTkFont(size=12)
        )
        self.percent_label.pack(pady=5)
    
    def update(self, value: int, message: str = None):
        """
        Met à jour la progression
        
        Args:
            value (int): Nouvelle valeur
            message (str): Nouveau message optionnel
        """
        self.current_value = value
        progress_value = value / self.max_value
        
        self.progress.set(progress_value)
        self.percent_label.configure(text=f"{int(progress_value * 100)}%")
        
        if message:
            self.message_label.configure(text=message)
        
        self.dialog.update()
    
    def close(self):
        """Ferme le dialogue"""
        self.dialog.destroy()