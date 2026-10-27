<?php
declare(strict_types=1);
// Web Push real: requiere composer install y claves VAPID en el entorno del servidor.
function enviar_push(PDO $db,int $usuarioId,int $id,string $titulo,string $descripcion,string $agente): void {
    $autoload=__DIR__.'/vendor/autoload.php';
    $publica=getenv('VAPID_PUBLIC_KEY') ?: '';
    $privada=getenv('VAPID_PRIVATE_KEY') ?: '';
    $subject=getenv('VAPID_SUBJECT') ?: '';
    if (!is_file($autoload) || !$publica || !$privada || !$subject) return;
    require_once $autoload;
    $push=new \Minishlink\WebPush\WebPush(['VAPID'=>['subject'=>$subject,'publicKey'=>$publica,'privateKey'=>$privada]]);
    $stmt=$db->prepare('SELECT endpoint,p256dh,auth FROM push_suscripciones WHERE usuario_id=?');
    $stmt->execute([$usuarioId]);
    foreach ($stmt->fetchAll() as $fila) {
        $sub=\Minishlink\WebPush\Subscription::create(['endpoint'=>$fila['endpoint'],'publicKey'=>$fila['p256dh'],'authToken'=>$fila['auth'],'contentEncoding'=>'aes128gcm']);
        $push->queueNotification($sub,json_encode(['id'=>$id,'title'=>$titulo,'body'=>mb_substr($descripcion,0,180),'agent'=>$agente,'url'=>'./?notificacion='.$id],JSON_UNESCAPED_UNICODE));
    }
    foreach ($push->flush() as $reporte) {
        if (!$reporte->isSuccess()) {
            if ($reporte->isSubscriptionExpired()) $db->prepare('DELETE FROM push_suscripciones WHERE endpoint=?')->execute([$reporte->getEndpoint()]);
            error_log('Push no entregado: '.$reporte->getReason());
        }
    }
}
