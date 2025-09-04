"""
Módulo de navegação adaptativa para aplicação TOTVS RM.

Este módulo fornece a classe RMAdaptNavigator que implementa navegação adaptativa
em elementos da interface gráfica do sistema TOTVS RM, com retry automático,
esperas inteligentes e tratamento robusto de erros para máxima resiliência.

A navegação adaptativa é essencial para automação robusta em sistemas como o RM,
onde elementos podem demorar para carregar ou estar temporariamente indisponíveis.

Classes:
    RMAdaptNavigator: Navegador principal com funcionalidades adaptativas

Funções:
    RMAdaptativeNavigator: Função de compatibilidade (deprecated)

Exemplo:
    Uso básico:
    
    >>> navigator = RMAdaptNavigator(parent_element)
    >>> element = navigator.navigate_to_element(
    ...     title="Salvar",
    ...     control_type="Button",
    ...     click_element=True
    ... )
    
    Navegação em sequência:
    
    >>> steps = [
    ...     ({"title": "Menu"}, False),
    ...     ({"auto_id": "btn_save"}, True)
    ... ]
    >>> success, text = navigator.navigate_to_path(steps)
"""

import logging
import time
from typing import Optional, Dict, Any, List, Tuple
from pywinauto.controls.hwndwrapper import HwndWrapper
from pywinauto.findwindows import ElementNotFoundError

from ..config.ui_config import get_ui_config
from ..exceptions.ui_exceptions import UIElementNotFoundError, UIInteractionError, UITimeoutError
from ..utils.screenshot import capture_screenshot_on_error
from .waits import UIWaits


logger = logging.getLogger(__name__)


class RMAdaptNavigator:
    """
    Navegador adaptativo para aplicação TOTVS RM.
    
    Esta classe implementa navegação adaptativa em elementos da interface gráfica
    do sistema TOTVS RM, fornecendo funcionalidades robustas para localização,
    interação e navegação sequencial em elementos de UI.
    
    A classe oferece retry com backoff exponencial, esperas inteligentes, validação
    de estado do elemento, tratamento de erros e captura de screenshots para 
    debugging, garantindo máxima resiliência na automação de interfaces gráficas.
    
    Attributes:
        parent_element (HwndWrapper): Elemento pai para navegação.
        config (UIConfig): Configurações de UI carregadas.
        waits (UIWaits): Utilitário para esperas inteligentes.
    """
    
    def __init__(self, parent_element: HwndWrapper) -> None:
        """
        Inicializa o navegador adaptativo com elemento pai.
        
        Args:
            parent_element (HwndWrapper): Elemento pai para as operações de navegação.
        
        Raises:
            ValueError: Se parent_element for None.
        """
        if parent_element is None:
            raise ValueError("Parâmetro 'parent_element' não pode ser None")
            
        self.parent_element = parent_element
        self.config = get_ui_config()
        self.waits = UIWaits()
    
    def navigate_to_element(
        self,
        title: Optional[str] = None,
        auto_id: Optional[str] = None,
        control_type: Optional[str] = None,
        click_element: bool = False,
        timeout: float = 0.5, # Mantido para compatibilidade, mas wait_timeout é preferível
        retry_interval: float = 1.0,
        max_retries: int = 5,
        wait_timeout: Optional[float] = None,
        wait_interval: Optional[float] = None
    ) -> HwndWrapper:
        """
        Navega para um elemento específico com retry adaptativo e backoff.
        
        Args:
            title (str, optional): Título do elemento.
            auto_id (str, optional): AutomationID do elemento.
            control_type (str, optional): Tipo de controle do elemento.
            click_element (bool, optional): Se deve clicar no elemento. Defaults to False.
            timeout (float, optional): DEPRECATED. Usado para compatibilidade.
            retry_interval (float, optional): Intervalo inicial para retries. Defaults to 1.0.
            max_retries (int, optional): Número máximo de tentativas. Defaults to 5.
            wait_timeout (float, optional): Timeout total para aguardar o elemento.
                Se None, usa retry_interval * max_retries. Defaults to None.
            wait_interval (float, optional): Intervalo de verificação. Se None, usa retry_interval.
        
        Returns:
            HwndWrapper: O elemento encontrado.
        
        Raises:
            UIElementNotFoundError: Se o elemento não for encontrado.
            UIInteractionError: Se houver erro na interação (ex: elemento desabilitado).
            UITimeoutError: Se o timeout for atingido.
            ValueError: Se nenhum critério de busca for fornecido.
        """
        if not any([title, auto_id, control_type]):
            raise ValueError("Pelo menos um critério (title, auto_id, control_type) deve ser fornecido")
        
        # MELHORIA: Validar se o elemento pai ainda existe
        if not self.parent_element.exists() or not self.parent_element.is_visible(): # type: ignore[attr-defined]
            raise UIElementNotFoundError("O elemento pai da navegação não existe ou não está mais visível.")

        try:
            action = "clicando" if click_element else "encontrando"
            criteria_log = f"Title: {title}, AutoID: {auto_id}, Type: {control_type}"
            logger.info(f"Navegando para elemento ({action}) - {criteria_log}")
            
            criteria = {k: v for k, v in [('title', title), ('auto_id', auto_id), ('control_type', control_type)] if v is not None}
            
            element_spec = self.parent_element.child_window(**criteria) # type: ignore[attr-defined]
            
            final_timeout = wait_timeout if wait_timeout is not None else (retry_interval * max_retries)
            final_interval = wait_interval if wait_interval is not None else retry_interval
            
            element = self._wait_for_element(element_spec, timeout=final_timeout, interval=final_interval)
            
            # MELHORIA: Validar estado do elemento antes da interação
            if not element.is_visible() or not element.is_enabled():
                error_msg = f"Elemento encontrado, mas não está em estado interativo (visível/habilitado): {criteria}"
                logger.error(error_msg)
                capture_screenshot_on_error("rm_adapt_navigator_element_not_interactive")
                raise UIInteractionError(error_msg)

            if click_element:
                element.draw_outline()
                time.sleep(self.config.wait_before_click)
                element.click_input()
                logger.debug(f"Elemento clicado com sucesso: {criteria}")
            else:
                element.draw_outline()
                logger.debug(f"Elemento eencontrado com sucesso: {criteria}")
            
            logger.info("Navegação adaptativa concluída com sucesso")
            return element
            
        except ElementNotFoundError as e:
            error_msg = f"Elemento não encontrado - {criteria_log}"
            logger.error(error_msg)
            capture_screenshot_on_error("rm_adapt_navigator_element_not_found")
            raise UIElementNotFoundError(error_msg, str(e)) from e
        
        except UITimeoutError as e:
            error_msg = f"Timeout ao esperar pelo elemento - {criteria_log}"
            logger.error(error_msg)
            # A captura de screenshot já é feita em _wait_for_element
            raise UITimeoutError(error_msg, str(e)) from e

        except Exception as e:
            error_msg = f"Erro inesperado durante navegação adaptativa: {e}"
            logger.error(error_msg)
            capture_screenshot_on_error("rm_adapt_navigator_failed")
            raise UIInteractionError(error_msg, str(e)) from e

    def navigate_to_path(self, steps: List[Tuple[Dict[str, Any], bool]]) -> Tuple[bool, str]:
        """Executa uma sequência de navegação com base em critérios.
        
        Args:
            steps (List[Tuple[Dict[str, Any], bool]]): Lista de tuplas onde cada tupla
                contém (criteria, do_click). O criteria é um dicionário com chaves
                como 'title', 'auto_id', 'control_type' e do_click é um boolean
                indicando se deve clicar no elemento.
        
        Returns:
            Tuple[bool, str]: Tupla contendo (success, last_identifier) onde:
                - success: True se toda a sequência foi executada com sucesso
                - last_identifier: Texto ou identificador do último elemento processado
        
        Raises:
            ValueError: Se a lista de steps estiver vazia ou contiver critérios inválidos.
            UIElementNotFoundError: Se o elemento pai não existir ou não estiver visível.
        
        Example:
            >>> navigator = RMAdaptNavigator(parent_element)
            >>> steps = [
            ...     ({"title": "Menu", "control_type": "MenuItem"}, False),
            ...     ({"auto_id": "btn_save"}, True)
            ... ]
            >>> success, last_text = navigator.navigate_to_path(steps)
            >>> if success:
            ...     print(f"Navegação concluída. Último elemento: {last_text}")
        """
        if not steps:
            raise ValueError("Lista de steps não pode estar vazia")
        
        # MELHORIA: Validar se o elemento pai ainda existe
        if not self.parent_element.exists() or not self.parent_element.is_visible(): # type: ignore[attr-defined]
            raise UIElementNotFoundError("O elemento pai da navegação não existe ou não está mais visível.")

        logger.info(f"Iniciando navegação em sequência com {len(steps)} passos")
        
        last_identifier = "UNKNOWN"
        
        for i, (criteria, do_click) in enumerate(steps):
            if not isinstance(criteria, dict) or not criteria:
                raise ValueError(f"Critérios inválidos no passo {i + 1}: {criteria}")
            
            title = criteria.get("title")
            auto_id = criteria.get("auto_id")
            control_type = criteria.get("control_type")
            last_identifier = title or auto_id or control_type or "UNKNOWN"

            logger.debug(f"Passo {i + 1}/{len(steps)} - {last_identifier}, Click: {do_click}")
            
            try:
                element = self.navigate_to_element(
                    title=title,
                    auto_id=auto_id,
                    control_type=control_type,
                    click_element=do_click
                )
                
                try:
                    last_identifier = element.window_text() or last_identifier
                except Exception:
                    pass  # Mantém o identificador dos critérios se a leitura falhar

            except (UIElementNotFoundError, UIInteractionError, UITimeoutError) as e:
                logger.warning(f"Navegação em sequência falhou no passo {i + 1} ({last_identifier}): {e}")
                capture_screenshot_on_error("rm_adapt_navigator_path_failed")
                return False, last_identifier
        
        logger.info(f"Navegação em sequência concluída com sucesso. Último elemento: {last_identifier}")
        return True, last_identifier
    
    def _wait_for_element(self, element_spec, timeout: float = 30.0, interval: float = 1.0):
        """Aguarda um elemento existir com estratégia de backoff exponencial e jitter.
        
        Args:
            element_spec: Objeto pywinauto WindowSpecification para o elemento a ser aguardado.
            timeout (float, optional): Tempo máximo de espera em segundos. Defaults to 30.0.
            interval (float, optional): Intervalo de espera inicial em segundos. Defaults to 1.0.
        
        Returns:
            WindowSpecification: O elemento encontrado e validado.
        
        Raises:
            UITimeoutError: Se o tempo limite for excedido sem encontrar o elemento.
        
        Note:
            Utiliza backoff exponencial com jitter para evitar picos de carga em
            execuções paralelas. O intervalo dobra a cada tentativa até um máximo
            de 10 segundos.
        
        Example:
            >>> element_spec = parent.child_window(title="Salvar")
            >>> found_element = self._wait_for_element(element_spec, timeout=60.0)
        """
        end_time = time.time() + timeout
        current_interval = interval
        attempts = 0
        
        logger.debug(f"Aguardando elemento por até {timeout}s (intervalo inicial: {interval}s com backoff)")
        
        while time.time() < end_time:
            attempts += 1
            try:
                if element_spec.exists():
                    logger.debug(f"Elemento encontrado após {attempts} tentativa(s).")
                    return element_spec
            except Exception as e:
                logger.debug(f"Tentativa {attempts} de encontrar elemento falhou: {e}")
            
            # Backoff exponencial com Jitter
            # Jitter previne picos de carga em execuções paralelas
            sleep_time = current_interval + random.uniform(0, 0.1 * current_interval)  # type: ignore[attr-defined]
            
            remaining_time = end_time - time.time()
            if remaining_time <= 0:
                break

            time.sleep(min(sleep_time, remaining_time))
            
            # Dobra o intervalo para a próxima tentativa, com um teto de 10 segundos
            current_interval = min(current_interval * 2, 10.0)

        error_msg = f"Elemento não encontrado após {timeout:.2f}s ({attempts} tentativas)."
        logger.error(error_msg)
        capture_screenshot_on_error("rm_adapt_navigator_wait_timeout")
        raise UITimeoutError(error_msg)
    
    def navigate_to_elements(self, *elements: Tuple[Dict[str, Any], bool]) -> Tuple[bool, str]:
        """Executa navegação em sequência usando argumentos individuais.
        
        Args:
            *elements: Argumentos variáveis de tuplas (criteria, do_click) onde:
                - criteria (Dict[str, Any]): Dicionário com critérios de busca
                - do_click (bool): Se deve clicar no elemento encontrado
        
        Returns:
            Tuple[bool, str]: Tupla contendo (success, last_identifier) onde:
                - success: True se toda a sequência foi executada com sucesso
                - last_identifier: Texto ou identificador do último elemento processado
        
        Example:
            >>> navigator = RMAdaptNavigator(parent_element)
            >>> success, text = navigator.navigate_to_elements(
            ...     ({"title": "Encargos", "control_type": "TabItem"}, True),
            ...     ({"title": "Salvar", "control_type": "Button"}, True)
            ... )
        """
        return self.navigate_to_path(list(elements))

def RMAdaptativeNavigator(
    parent,
    title=None,
    auto_id=None,
    control_type=None,
    click_element: bool = True,
    timeout: float = 0.5,
    retry_interval: float = 1.0,
    max_retries: int = 5,
    **kwargs: Any
):
    """Função de compatibilidade para navegação adaptativa (DEPRECATED).
    
    Warning:
        Esta função está marcada como deprecated. Use a classe RMAdaptNavigator.
    
    Args:
        parent: Elemento pai para navegação.
        title (str, optional): Título do elemento a ser encontrado.
        auto_id (str, optional): ID automático do elemento.
        control_type (str, optional): Tipo de controle do elemento.
        click_element (bool, optional): Se deve clicar no elemento. Defaults to True.
        timeout (float, optional): Timeout para encontrar elemento. Defaults to 0.5.
        retry_interval (float, optional): Intervalo entre tentativas. Defaults to 1.0.
        max_retries (int, optional): Número máximo de tentativas. Defaults to 5.
        **kwargs: Argumentos adicionais para compatibilidade futura.
    
    Returns:
        WindowSpecification: Elemento encontrado.
    
    Raises:
        ValueError: Se ocorrer erro durante a navegação.
    
    Example:
        >>> # DEPRECATED - Use RMAdaptNavigator ao invés
        >>> element = RMAdaptativeNavigator(
        ...     parent_element,
        ...     title="Salvar",
        ...     control_type="Button"
        ... )
    """
    import warnings
    warnings.warn(
        "A função RMAdaptativeNavigator está obsoleta. Use a classe RMAdaptNavigator diretamente.",
        DeprecationWarning,
        stacklevel=2
    )
    
    try:
        navigator = RMAdaptNavigator(parent)
        # Passa os novos parâmetros se eles forem fornecidos via kwargs
        return navigator.navigate_to_element(
            title=title,
            auto_id=auto_id,
            control_type=control_type,
            click_element=click_element,
            timeout=timeout, # Mantido para compatibilidade
            retry_interval=retry_interval,
            max_retries=max_retries,
            wait_timeout=kwargs.get("wait_timeout"),
            wait_interval=kwargs.get("wait_interval")
        )
    except (UIElementNotFoundError, UIInteractionError, UITimeoutError, ValueError) as e:
        # Mantém a compatibilidade do tipo de erro levantado
        raise ValueError(str(e)) from e
    except Exception as e:
        # Captura outras exceções inesperadas
        raise ValueError(f"Erro inesperado na função de compatibilidade: {e}") from e


# Exemplo de uso
if __name__ == "__main__":
    """
    Exemplos de uso do RMAdaptNavigator.
    
    Este bloco demonstra diferentes formas de usar o navegador adaptativo
    para automação robusta de interfaces TOTVS RM, incluindo navegação
    individual e sequencial.
    
    Os exemplos estão comentados para evitar execução acidental, mas
    mostram padrões de uso recomendados para diferentes cenários.
    """
    try:
        # Assumindo que você tem um parent_element
        # navigator = RMAdaptNavigator(parent_element)
        
        # Navegar para elemento específico
        # element = navigator.navigate_to_element(
        #     title="Salvar",
        #     control_type="Button",
        #     max_retries=3
        # )
        
        # Navegar em sequência
        # steps = [
        #     ({"title": "Menu"}, False),
        #     ({"auto_id": "btn_save"}, True)
        # ]
        # success, text = navigator.navigate_to_path(steps)
        
        # Ou usar navigate_to_elements para mais conveniência
        # tab_criteria = {"title": "Encargos", "control_type": "TabItem"}
        # btn_criteria = {"title": "Salvar", "control_type": "Button"}
        # success, text = navigator.navigate_to_elements(
        #     (tab_criteria, True),
        #     (btn_criteria, True)
        # )
        
        print("Exemplo de uso do RMAdaptNavigator")
        print("Navegação adaptativa com retry automático")
        
    except Exception as e:
        print(f"Erro no exemplo: {e}")